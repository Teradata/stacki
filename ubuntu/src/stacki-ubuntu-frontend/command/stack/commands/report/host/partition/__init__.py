# @SI_Copyright@
# @Copyright@

import shlex
import stack.api
from stack.exception import *

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	Run a command for each specified host.

	<arg optional='0' type='string' name='host'>
	Host name of the machine that needs to be partitioned.
	</arg>

	<param type='boolean' name='bootDisk' optional='0'>
	Specify if we want only the partman recipe for boot disk.
	</param>

	<param type='boolean' name='nukedisks' optional='0'>
	Specify if we want to wipe disks or not.
	</param>

	<example cmd='report host partition backend-0-0 bootDisk=True'>
	Output the boot disk partition recipe for backend-0-0 without
	wiping all partitions.
	</example>

	<example cmd='report host partition backend-0-1 bootDisk=False nukedisks=True'>
	Output the partition commands for non boot disks on this machine and wipe all
	partitions on them.
	</example>
	"""

	#
	# Arrange partition dictionary based off disk
	# E.g. {'sda': [{'/'...}, {'/var'...}]
	#
	def build_partition_dict(self, data):
		partition_dict = {}
		bootdisk = None
		
		for d in data:
        		dev   = d['device']
			mntpt = d['mountpoint']

			if dev not in partition_dict:
				partitions = []
			else:
				partitions = partition_dict[dev]

			partitions.append(d)
			partition_dict[dev] = partitions

			if mntpt in ['/', '/boot']:
				self.bootdisk = dev

		return partition_dict

	# Generate recipe for Ubuntu book disk
	def create_bootdisk_recipe(self, bootdisk_partitions, nukedisks):
		recipe = []
		recipe.append('root ::')

		# TODO: Get min size from attribute?
		min_size = 10240
		boot_set = False

		for p in bootdisk_partitions:
			mntpt = p['mountpoint']
			fstype = p['fstype']
			options = p['options']
			size = p['size']
			part_id = p['partid']
			format_flag = 'swap'
			priority = min_size + 100 + part_id

			# Fill rest of the disk with this partition			
			if size == 0:
				size = -1

			recipe.append('%d %d %d %s' % \
				(min_size, priority, size, fstype))

			if mntpt in ['/', '/boot'] and not boot_set:
				recipe.append('$bootable{ } $primary{ }')
				boot_set = True

			if 'primary' in options:
				recipe.append('$primary{ }')

			if mntpt not in 'swap':
				recipe.append('use_filesystem{ } filesystem{ %s }' \
					 % fstype)
				format_flag = 'format'

			if not nukedisks and \
				mntpt not in ['/', '/boot', '/var', 'swap'] and \
				'swap' not in fstype:
				recipe.append('method{ keep }')
			else:
				recipe.append('method{ %s } format{ }' \
					% format_flag)
			recipe.append('mountpoint{ %s }' % mntpt)
			recipe.append('.')

		return recipe

	# Generate late commands to partition non-boot disks
	def generate_late_cmd(self, partition_dict, nukedisks):
		late_cmd = []

		#
		# If we are not wiping the disk, copy the contents of
		# /etc/fstab from previous install into current
		# /etc/fstab (Except for /, /boot, /var)
		#
		if not nukedisks:
			late_cmd.append('cat /tmp/old_etc_fstab.txt >> ' \
				'/target/etc/fstab')
			return late_cmd

		for disk in partition_dict:
			partition_list = partition_dict[disk]
			sorted_partition_list = \
				sorted(partition_list, key=lambda k: k['partid'])
			
			# Wipe partition table if nukedisks=true
#			late_cmd.append('in-target /bin/dd if=/dev/zero of=/dev/%s ' \
#					'count=512 bs=1' % disk)

			late_cmd.append('in-target /sbin/parted -s' \
				' /dev/%s mklabel gpt' % disk)
			start = 0
			start_str = '0%'

			for p in sorted_partition_list:
				mntpt   = p['mountpoint']
				fstype  = p['fstype']
				options = p['options']
				size    = int(p['size'])
				part_id = p['partid']
				device  = p['device']
				disk_partition = device + str(part_id)
				end = start + size
				end_str = str(end) + 'MB'
				primary = ''
				fs_options = ''
				mnt_options = 'defaults 0 0'

				options_arr = shlex.split(options)
				for o in options_arr:
					if '--is_primary' in o:
						primary = 'primary'
					elif '--fs_options=' in o:
						fs_options = o.replace('--fs_options=','')
					elif '--mnt_options' in o:
						mnt_options = o.replace('--mnt_options=', '') 

				if size == 0:
					end_str = '100%'

				late_cmd.append('in-target /sbin/parted -s ' \
					'/dev/%s mkpart %s %s %s %s' %       \
                        		(device, primary, fstype, start_str, end_str))

				cmd = 'export DEVNAME=`/target/bin/lsblk /dev/%s' % device
				cmd += ' -ro NAME | /target/usr/bin/tail -1`'
				late_cmd.append(cmd)

				if fstype == 'xfs':
					late_cmd.append('in-target /sbin/mkfs -t %s ' \
						'%s -f /dev/$DEVNAME' % (fstype,fs_options))
				else:
					late_cmd.append('in-target /sbin/mkfs -t %s ' \
						'%s -F /dev/$DEVNAME' % (fstype,fs_options))

				late_cmd.append('in-target /bin/mkdir -p %s' \
					% mntpt)
				late_cmd.append('/bin/echo ' 			\
					'"/dev/$DEVNAME %s %s %s" >> ' \
					'/target/etc/fstab' % 		 	\
					(mntpt, fstype, mnt_options))
				start = end
				start_str = end_str

		return late_cmd

	def run(self, params, args):
		# Parse Params
		(bootDiskF, nukedisks) = self.fillParams([
                        ('bootDisk', None, True),
			('nukedisks', None, False)
		])

		bootDiskF = self.str2bool(bootDiskF)
		nukedisks = self.str2bool(nukedisks)

		# Get host to run the command on
		hosts = self.getHostnames(args)
		result = None
		self.bootdisk = None

		for host in hosts:
			if self.getHostAttr(host,'os') != 'ubuntu':
				raise CommandError(self, "This is not ubuntu")

			result = self.call('list.storage.partition', ['output-format=json', host])

			if not result:
				#try the appliance
				appliance = self.getHostAttr(host,'appliance')
				result = self.call('list.storage.partition', 
						['output-format=json', appliance])
			# good god, default to something
			if not result:
				result = [{"partid": 2, "fstype": "swap", "mountpoint": "swap", 
					"device": "sda", "scope": "backend-0-0", "options": "", 
					"size": 16000}, {"partid": 4, "fstype": "xfs", 
					"mountpoint": "/state/partition1", "device": "sda", 
					"scope": "backend-0-0", 
					"options": "--primary=1 \
					--mnt_options=\"async auto\" --fs_options=\"nosuid\""
					, "size": 0}, 
					{"partid": 1, "fstype": "xfs", "mountpoint": "/", 
					"device": "sda", "scope": "backend-0-0", "options": "",
					"size": 20000}, 
					{"partid": 3, "fstype": "xfs", "mountpoint": "/var", 
					"device": "sda", "scope": "backend-0-0", 
					"options": "", "size": 25000}]
		
		part_dict = self.build_partition_dict(result)

		if bootDiskF:
			bootdisk_part = part_dict[self.bootdisk]
			#
			# Sort partitions based on partid column since the partitions
			# will be created in the order that is specified in the recipe file
			#
			sorted_partitions = sorted(bootdisk_part, key=lambda k: k['partid'])		
			recipe = self.create_bootdisk_recipe(sorted_partitions, nukedisks)
			print(' \\\n'.join(recipe))
		else:
			part_dict.pop(self.bootdisk, None)
			late_cmds = self.generate_late_cmd(part_dict, nukedisks)
			print(';'.join(late_cmds) + ';')
