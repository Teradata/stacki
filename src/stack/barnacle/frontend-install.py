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

def banner(string):
	print('#######################################')
	print(string)
	print('#######################################')	

def copy(source, dest):
	banner("Copying %s to local disk" % source)
	subprocess.call(['mkdir', '-p', dest])
	subprocess.call(['mount', '-o', 'loop', source, '/media'])
	subprocess.call(['cp', '-r', '/media/.', dest])
	subprocess.call(['umount', '/media'])

def mount(source, dest):
	subprocess.call(['mkdir', '-p', dest])
	subprocess.call(['mount', '-o', 'loop', source, dest])

def umount(dest):
	subprocess.call(['umount', dest])

def installrpms(pkgs):
	cmd = [ 'yum', '-y', 'install' ]
	cmd += pkgs
	subprocess.call(cmd)

def generate_multicast():
	a = random.randrange(225,240)
	# Exclude 232
	while a == 232:
		a = random.randrange(225,240)
	b = random.randrange(1,255)
	c = random.randrange(1,255)
	d = random.randrange(1,255)
	return str(a)+'.'+str(b)+'.'+str(c)+'.'+str(d)

def repoconfig(ccmnt, ccname, ccver, osmnt):
	subprocess.call('mv /etc/yum.repos.d/*.repo /tmp/', shell = True)

	file = open('/etc/yum.repos.d/stack.repo', 'w')
	file.write('[stacki]\n')
	file.write('name=stacki\n')
	file.write('baseurl=file://%s/%s/%s/redhat/x86_64\n'
		% (ccmnt, ccname, ccver))
	file.write('assumeyes=1\n')
	file.write('gpgcheck=no\n')
	file.write('[OS]\n')
	file.write('name=OS\n')
	file.write('baseurl=file://%s\n' % osmnt)
	file.write('assumeyes=1\n')
	file.write('gpgcheck=no\n')
	file.close()

	
def ldconf():
	file = open('/etc/ld.so.conf.d/foundation.conf', 'w')
	file.write('/opt/stack/lib\n')
	file.close()

	subprocess.call(['ldconfig'])

def usage():
	print("Requried arguments:")
	print("\t--stacki-iso=ISO : path to stacki ISO")
	print("\t--stacki-version=version : stacki version")
	print("\t--stacki-name=name : stacki name (usually 'stacki')")
	print("\t--os-iso=ISO1,ISO2 : path(s) to OS ISO(s)")
	print("\t--os-version=version : OS version")
	print("\t--os-name=name : OS name (e.g., 'CentOS')")

	print()
	print("Optional arguments:")
	print("\t--noX : Don't require X11 for frontend wizard. Use text mode")
	sys.exit(-1)

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
	'os-iso=', 'os-version=', 'os-name=', 'noX' ]) 

stacki_iso = None
stacki_version = None
stacki_name = None
os_iso = None
os_version = None
os_name = None
noX = 0
no_net_reconfig = 0

for opt, arg in opts:
	if opt == '--stacki-iso':
		stacki_iso = arg.split(',')
	elif opt == '--stacki-version':
		stacki_version = arg
	elif opt == '--stacki-name':
		stacki_name = arg
	elif opt == '--os-iso':
		os_iso = arg.split(',')
	elif opt == '--os-version':
		os_version = arg
	elif opt == '--os-name':
		os_name = arg
	elif opt == '--noX':
		noX = 1

if not stacki_iso:
	print('--stacki-iso is not specified\n')
	usage()
	sys.exit(-1)

if not stacki_version:
	print('--stacki-version is not specified\n')
	usage()
	sys.exit(-1)

if not stacki_name:
	print('--stacki-name is not specified\n')
	usage()
	sys.exit(-1)

if not os_iso:
	print('--os-iso is not specified\n')
	usage()
	sys.exit(-1)

if not os_version:
	print('--os-version is not specified\n')
	usage()
	sys.exit(-1)

if not os_name:
	print('--os-name is not specified\n')
	usage()
	sys.exit(-1)

ccname = stacki_name
ccver = stacki_version
cciso = stacki_iso[0]
osname = os_name
osver = os_version
osiso1 = os_iso[0]
if len(os_iso) > 1:
	osiso2 = os_iso[1]
else:
	osiso2 = None

if not os.path.exists(cciso):
	print("Error: File '{0}' does not exist.".format(cciso))
	exit()
if not os.path.exists(osiso1):
	print("Error: File '{0}' does not exist.".format(osiso1))
	exit()
if osiso2 and not os.path.exists(osiso2):
	print("Error: File '{0}' does not exist.".format(osiso2))
	exit()

banner("Boostrap Stack Command Line")

# turn off NetworkManager so it doesn't overwrite our networking info
subprocess.call(['service', 'NetworkManager', 'stop'])

# copy the isos
ccdest = '/export/stack/pallets'
copy(cciso, ccdest)

osdest = '/export/stack/pallets/%s' % osname
copy(osiso1, osdest)
if osiso2:
	copy(osiso2, osdest)

# create repo config file
repoconfig(ccdest, ccname, ccver, osdest)

# install rpms
pkgs = [ 'stack-command', 'foundation-python', 'stack-pylib',
	'foundation-python-xml', 'foundation-redhat', 'deltarpm', 
	'python-deltarpm', 'createrepo', 'foundation-py-wxPython',
	'stack-wizard', 'net-tools', 'foundation-py-pygtk' ]
installrpms(pkgs)

banner("Configuring dynamic linker for stacki")
ldconf()

if not os.path.exists('/tmp/site.attrs') and not \
		os.path.exists('/tmp/rolls.xml'):
	#
	# execute boss_config.py. completing this wizard creates
	# /tmp/site.attrs and /tmp/rolls.xml
	#
	banner("Launch Boss-Config")
	mount(cciso, '/mnt/cdrom')
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
	
banner("Generate XML")
# run stack list node xml server attrs="<python dict>"
stackpath = '/opt/stack/bin/stack'
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
subprocess.call([stackpath, 'run', 'pallet'], stdin=infile, stdout=outfile)
infile.close()
outfile.close()

banner("Run Setup Script")
# run run.sh
subprocess.call(['sh', '/tmp/run.sh'])

# before we add the pallets, clean up the old OS that we copied to the disk
subprocess.call(['/bin/rm', '-rf', osdest])

banner("Adding Pallets")
subprocess.call([stackpath, 'add', 'pallet', cciso])
subprocess.call([stackpath, 'add', 'pallet', osiso1])
if osiso2:
	subprocess.call([stackpath, 'add', 'pallet', osiso2])
subprocess.call([stackpath, 'enable', 'pallet', '%'])

# all done
banner("Done")

print("Reboot to complete process.")

