# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.OSArgumentProcessor, stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor, stack.commands.Plugin):

	"""
	Plugin that invokes 'stack add storage partition' and adds
	the partitions to the database.
	"""
	def provides(self):
		return 'default'


	def run(self, args):
		hosts = args
		for host in hosts.keys():
			#
			# first remove the entries for this host
			#
			if host == 'global':
				self.owner.call('remove.storage.partition', ['scope=global','device=*'])
			else:
				try:
					_ = self.getOSNames([host])
					self.owner.call('remove.os.storage.partition', [host])
				except:
					pass

				try:
					_ = self.getApplianceNames([host])
					self.owner.call('remove.appliance.storage.partition', [host])
				except:
					pass

				try:
					_ = self.getHostnames([host])
					self.owner.call('remove.host.storage.partition', [host])
				except:
					pass

			# Get list of devices for this host
			devices = []
			for d in hosts[host].keys():
				devices.append(d)
			devices.sort()

			# Loop through all devices in the list
			for device in devices:
				partition_list = hosts[host][device]

				# Add storage partitions for this device
				for partition in partition_list:
					cmdargs = []
					if host != 'global':
						cmdargs.append(host)
					cmdargs += [ 'device=%s' % device ]

					mountpt = partition['mountpoint']
					size = partition['size']
					parttype = partition['type']
					options = partition['options']
					partid = partition['partid']

					if mountpt:
						cmdargs.append('mountpoint=%s' % mountpt)
					if parttype:
						cmdargs.append('type=%s' % parttype)

					cmdargs.append('size=%s' % size)
					if options:
						cmdargs.append('options=%s' % options)
					if partid:
						cmdargs.append('partid=%s' % partid)

					self.owner.call('add.storage.partition',
						cmdargs)
