#!/opt/stack/bin/python

import os
import sys
import stack.pallet
import stack.roll
import stack.installcgi

#
# make sure the DVD is mounted
#
cmd = 'mkdir -p /mnt/cdrom ; mount /dev/cdrom /mnt/cdrom'
os.system(cmd)

cmd = 'rm -f /install ; ln -s /mnt/sysimage/export/stack /install'
os.system(cmd)

icgi = stack.installcgi.InstallCGI(rootdir='/mnt/sysimage/export/stack')
g = stack.roll.Generator()
getpallet = stack.pallet.GetPallet()

filename = None
if os.path.exists('/tmp/pallets.xml'):
	filename = '/tmp/pallets.xml'
elif os.path.exists('/tmp/rolls.xml'):
	filename = '/tmp/rolls.xml'

if not filename:
	if 0:
		#
		# XXX not sure if we need to do this
		#
		media = stack.media.Media()
		if media.mounted():
			media.ejectCD()

	sys.exit(0)

g.parse(filename)
pallets = g.rolls

getpallet.downloadDVDPallets(pallets)
getpallet.downloadNetworkPallets(pallets)

cwd = os.getcwd()
os.chdir('/mnt/sysimage/export/stack')
icgi.rebuildDistro(pallets)
os.chdir(cwd)

cmd = 'rm -f /install ; ln -s /mnt/sysimage/export/stack /install'
os.system(cmd)

#
# added the code below for 7.x
#
cmd = '/bin/yum -c /tmp/anaconda-yum.conf clean all'
os.system(cmd)

#
# write a new repo file for our distro
#
os.system('mkdir -p /tmp/yum.repos.d')
file = open('/tmp/yum.repos.d/stacki.repo', 'w')
file.write('[stacki]\n')
file.write('name=stacki\n')
file.write('baseurl=file:///install/distributions/default/x86_64\n')
file.close()
