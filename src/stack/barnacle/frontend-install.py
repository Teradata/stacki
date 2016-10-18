#!/usr/bin/python

# Things the RPM will do:
# Copy foundation.conf to /etc/ld.so.conf.d/
# Copy boss-config files to /opt/stack/bin.  Boss_config.py 
# has to be changed to accomodate lack of database
# Copy wxpython RPM somewhere (it isnt included in 6.6)

from __future__ import print_function
import os
import sys
import string
import subprocess
import random
import getopt
import tempfile

def banner(string):
	print('#######################################')
	print(string)
	print('#######################################')	

def copy(source, dest):
	isodir = tempfile.tempdir()
	banner("Copying %s to local disk" % source)
	subprocess.call(['mkdir', '-p', dest])
	subprocess.call(['mount', '-o', 'loop', source, isodir])
	subprocess.call(['cp', '-r', isodir, dest])
	subprocess.call(['umount', isodir])

def mount(source, dest):
	subprocess.call(['mkdir', '-p', dest])
	subprocess.call(['mount', '-o', 'loop', source, dest])

def umount(dest):
	subprocess.call(['umount', dest])

def installrpms(pkgs):
	cmd = [ 'yum', '-y', 'install' ]
	cmd += pkgs
	return subprocess.call(cmd)

def generate_multicast():
	a = random.randrange(225,240)
	# Exclude 232
	while a == 232:
		a = random.randrange(225,240)
	b = random.randrange(1,255)
	c = random.randrange(1,255)
	d = random.randrange(1,255)
	return str(a)+'.'+str(b)+'.'+str(c)+'.'+str(d)

def repoconfig(mountdir):

	for (r, d, f) in os.walk(mountdir):
		for name in f:
			if name == 'roll-stacki.xml':
				repodir = r
				break

	file = open('/etc/yum.repos.d/stack.repo', 'w')
	file.write('[stacki]\n')
	file.write('name=stacki\n')
	file.write('baseurl=file://%s\n'
		% (repodir))
	file.write('assumeyes=1\n')
	file.write('gpgcheck=no\n')
	file.close()

	
def ldconf():
	file = open('/etc/ld.so.conf.d/foundation.conf', 'w')
	file.write('/opt/stack/lib\n')
	file.close()

	subprocess.call(['ldconfig'])

def usage():
	print("Required arguments:")
	print("\t--stacki-iso=ISO : path to stacki ISO")
	print("\t--stacki-version=version : stacki version")
	print("\t--stacki-name=name : stacki name (usually 'stacki')")
	print("Optional arguments:")
	print("\t--extra-iso=iso1,iso2,iso3.. : list of pallets to add")
	print("\t--noX : Don't require X11 for frontend wizard. Use text mode")

##
## MAIN
##

#
# log all output to a file too
#
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

tee = subprocess.Popen(["tee", "/tmp/frontend-install.log"],
	stdin=subprocess.PIPE)
os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
os.dup2(tee.stdin.fileno(), sys.stderr.fileno())

#
# process the command line arguments
#
opts, args = getopt.getopt(sys.argv[1:], '', [
	'stacki-iso=', 'stacki-version=', 'stacki-name=',
	'extra-iso=', 'noX' ]) 

stacki_iso = None
extra_iso = []
noX = 0

for opt, arg in opts:
	if opt == '--stacki-iso':
		stacki_iso = arg
	elif opt == '--extra-iso':
		extra_iso = arg.split(',')
	elif opt == '--noX':
		noX = 1

if not stacki_iso:
	print('--stacki-iso is not specified\n')
	usage()
	sys.exit(-1)

if not os.path.exists(stacki_iso):
	print("Error: File '{0}' does not exist.".format(stacki_iso))
	sys.exit(1)

for iso in extra_iso:
	if not os.path.exists(iso):
		print("Error: File '{0}' does not exist.".format(iso))
		sys.exit(1)

banner("Boostrap Stack Command Line")

# turn off NetworkManager so it doesn't overwrite our networking info
subprocess.call(['service', 'NetworkManager', 'stop'])

stacki_iso = os.path.abspath(stacki_iso)

mountdir = tempfile.mkdtemp()
mount(stacki_iso, mountdir)

# create repo config file
repoconfig(mountdir)

pkgs = [ 'stack-command', 'foundation-python', 'stack-pylib',
	'foundation-python-xml', 'foundation-redhat', 
	'foundation-py-wxPython','foundation-py-pygtk',
	'stack-wizard', 'net-tools']

return_code = installrpms(pkgs)
if return_code != 0:
	print("Error: stacki package installation failed")
	sys.exit(return_code)

banner("Configuring dynamic linker for stacki")
ldconf()

if not os.path.exists('/tmp/site.attrs') and not \
		os.path.exists('/tmp/rolls.xml'):
	#
	# execute boss_config.py. completing this wizard creates
	# /tmp/site.attrs and /tmp/rolls.xml
	#
	banner("Launch Boss-Config")
	mount(stacki_iso, '/mnt/cdrom')
	cmd = [ '/opt/stack/bin/python', '/opt/stack/bin/boss_config.py',
		'--no-partition', '--no-net-reconfig' ]
	if noX:
		cmd.append('--noX')
	subprocess.call(cmd)
	umount('/mnt/cdrom')
	
	# add missing attrs to site.attrs
	f = open("/tmp/site.attrs", "a")
	string= "Kickstart_PrivateKickstartBasedir:distributions\n"
	string+= "Kickstart_Multicast:"+generate_multicast()+"\n"
	string+= "Private_PureRootPassword:a\n"
	string+= "Confirm_Private_PureRootPassword:a\n"
	string+= "Server_Partitioning:force-default-root-disk-only\n"
	string+= "disableServices:\n"
	string+= "serviceList:\n"
	f.write(string)
	f.close()

# convert site.attrs to python dict
f = [line.strip() for line in open("/tmp/site.attrs","r")]
attributes = {}
for line in f:
        split = line.split(":",1)
        attributes[split[0]]=split[1]
	
# fix hostfile
f = open("/etc/hosts", "a")
line = '%s\t%s %s\n' % (attributes['Kickstart_PrivateAddress'],
	attributes['Kickstart_PrivateHostname'], attributes['Info_FQDN'])
f.write(line)
f.close()

# set the hostname to the user-entered FQDN
print('Setting hostname to %s' % attributes['Info_FQDN'])
subprocess.call(['hostname', attributes['Info_FQDN']])

stackpath = '/opt/stack/bin/stack'
subprocess.call([stackpath, 'add', 'pallet', stacki_iso])
banner("Generate XML")
# run stack list node xml server attrs="<python dict>"
f = open("/tmp/stack.xml", "w")
cmd = [ stackpath, 'list', 'node', 'xml', 'server',
	'attrs={0}'.format(repr(attributes))]
print('cmd: %s' % ' '.join(cmd))
subprocess.call(cmd, stdout=f, stderr=None)
f.close()

banner("Process XML")
# pipe that output to stack run pallet and output run.sh
infile = open("/tmp/stack.xml", "r")
outfile = open("/tmp/run.sh", "w")
subprocess.call([stackpath, 'run', 'pallet', 'database=false'], stdin=infile,
	stdout=outfile)
infile.close()
outfile.close()

banner("Run Setup Script")
# run run.sh
subprocess.call(['sh', '/tmp/run.sh'])

banner("Adding Pallets")
subprocess.call([stackpath, 'add', 'pallet', stacki_iso])
for iso in extra_iso:
	iso = os.path.abspath(iso)
	subprocess.call([stackpath, 'add', 'pallet', iso])
subprocess.call([stackpath, 'enable', 'pallet', '%'])

# all done
banner("Done")

print("Reboot to complete process.")

