#!/opt/stack/bin/python
import subprocess
import tempfile
import shlex

from stack.commands import *

sys.path.append('/tmp')
from stack_site import *

def getDisks():
	cmd = "list-devices disk"
	p = subprocess.Popen(cmd.split(), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	o, e = p.communicate()
	disks = o.split()
	return disks

def getSavedPartitions(disks):
	fstab_contents = None

	# Search for /etc/fstab
	for disk in disks:
		cmd = "lsblk -nro NAME %s" % disk
		p = subprocess.Popen(cmd.split(), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		parts = p.communicate()[0].split()

		for part in parts:
			partname = '/dev/' + part
			if partname == disk:
				continue
			tmpfile = tempfile.mkdtemp()
			# Mount file
			cmd = "lsblk -nro FSTYPE %s" % partname
                	p = subprocess.Popen(cmd.split(), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			fstype = p.communicate()[0].split()[0]
			mnt = 'mount -t %s %s %s' % (fstype, partname, tmpfile)
			os.system(mnt)
			fstab_path = tmpfile + '/etc/fstab'

			try:
				f = open(fstab_path, 'r')
				fstab_contents = f.readlines()
				f.close()
			except:
				pass

			umnt = 'umount %s' % tmpfile
			umnt_p = subprocess.Popen(umnt.split(), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

			rmdir = 'rm -rf %s' % tmpfile
			rmdir_p = subprocess.Popen(rmdir.split(), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
			if fstab_contents:
				return fstab_contents
				break

		if fstab_contents:
			return fstab_contents
			break

def processOldFstab(fstab_contents):
	old_fstab = open('/tmp/old_etc_fstab.txt', 'w+')

	for line in fstab_contents:
		# Ignore comments
		if line.startswith('#'):
			continue
		fstab_entry = line.split()

		if line and len(fstab_entry) > 4:
			mntpt  = fstab_entry[1].strip()
			fstype = fstab_entry[2].strip()
			#
			# Write entry to fstab only if mountpoint not in
			# /, /var/, /boot
			#
			if mntpt not in ['/', '/var', '/boot', 'swap'] and \
				fstype not in ['swap']:
				old_fstab.write(line)

	old_fstab.close()

def getNukes(host_disks, s):
	disks = []

	if s and s.upper() in [ 'ALL', 'YES', 'Y', 'TRUE', '1' ]:
		disks = host_disks
	elif s and s.upper() in ['NONE', 'NO', 'N', 'FALSE', '0' ]:
                disks = []
	elif s:
		#
		# validate the user input for nukedisks -- that is, make sure 
		# the disks specified by the user are actually on this machine
		#
		for disk in s.split():
			if disk in host_disks:
				disks.append(disk)

	return disks


def nukeIt(disk):
	#
	# Clear out the master boot record of the drive
	#
	FNULL = open(os.devnull, 'w')

	if attributes.has_key('disklabel'):
		disklabel = attributes['disklabel']
	else:
		disklabel = 'gpt'

        cmd = 'dd if=/dev/zero of=/dev/%s count=512 bs=1' % disk
#        cmd = '/sbin/wipefs -a %s' % disk
	subprocess.call(shlex.split(cmd),
		stdout = FNULL, stderr = subprocess.STDOUT)

	cmd = 'parted -s /dev/%s mklabel %s' % (disk, disklabel)
	subprocess.call(shlex.split(cmd),
		stdout = FNULL, stderr = subprocess.STDOUT)

	FNULL.close()
	return



disks = getDisks()

if str2bool(attributes['nukedisks']) == False:
	fstab_contents = getSavedPartitions(disks)
	processOldFstab(fstab_contents)
else:
	for disk in disks:
		nukeIt(disk)
