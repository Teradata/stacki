#!/usr/bin/python

# Things the RPM will do:
# Copy foundation.conf to /etc/ld.so.conf.d/
# Copy boss-config files to /opt/stack/bin.  Boss_config.py 
# has to be changed to accomodate lack of database
# Copy wxpython RPM somewhere (it isnt included in 6.6)

import os
import sys
import string
import subprocess
import random

def banner(string):
	print '#######################################'
	print string
	print '#######################################'	

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
	cmd = [ 'yum', '-y', '-c', '/tmp/barnacle.repo', '--disablerepo=*' ]
	cmd += [ '--enablerepo=stacki,OS', 'install' ]
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

def repoconfig(ccmnt, osmnt):
	file = open('/tmp/barnacle.repo', 'w')
	file.write('[stacki]\n')
	file.write('name=stacki\n')
	file.write('baseurl=file://%s\n' % ccmnt)
	file.write('assumeyes=1\n')
	file.write('gpgcheck=no\n')
	file.write('[OS]\n')
	file.write('name=OS\n')
	file.write('baseurl=file://%s\n' % osmnt)
	file.write('assumeyes=1\n')
	file.write('gpgcheck=no\n')
	file.close()

	subprocess.call('mv /etc/yum.repos.d/*.repo /tmp/', shell = True)
	
	file = open('/etc/yum.repos.d/stack.repo' ,'w')
	file.write('[Stack]\n')
	file.write('name=Stack\n')
	file.write('baseurl=file:///export/stack/distributions/default/x86_64\n')
	file.write('assumeyes=1\n')
	file.write('gpgcheck=no\n')
	file.close()

def ldconf():
	file = open('/etc/ld.so.conf.d/foundation.conf', 'w')
	file.write('/opt/stack/lib\n')
	file.close()

	subprocess.call(['ldconfig'])

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
print sys.argv[1:]
if len(sys.argv[1:]) != 6 and len(sys.argv[1:]) != 7:
	print "Requires 6 arguments and 1 optional argument, in order:"
	print "\tstacki short name (usually 'stacki')"
	print "\tstacki version"
	print "\tpath to stacki ISO"
	print "\tOS short name (eg 'CentOS')"
	print "\tOS version"
	print "\tpath to OS ISO DVD1"
	print "\t(optional path to OS ISO DVD2)"
	exit()

ccname = sys.argv[1]
ccver = sys.argv[2]
cciso = sys.argv[3]
osname = sys.argv[4]
osver = sys.argv[5]
osiso1 = sys.argv[6]
if len(sys.argv[1:]) == 7:
	osiso2 = sys.argv[7]
else:
	osiso2 = None

if not os.path.exists(cciso):
	print "Error: File '{0}' does not exist.".format(cciso)
	exit()
if not os.path.exists(osiso1):
	print "Error: File '{0}' does not exist.".format(osiso1)
	exit()
if osiso2 and not os.path.exists(osiso2):
	print "Error: File '{0}' does not exist.".format(osiso2)
	exit()

banner("Boostrap Stack Command Line")

# turn off NetworkManager so it doesn't overwrite our networking info
subprocess.call(['service', 'NetworkManager', 'stop'])

# copy the isos
ccdest = '/export/%s' % ccname
copy(cciso, ccdest)
osdest = '/export/%s' % osname
copy(osiso1, osdest)
if osiso2:
	copy(osiso2, osdest)

# create repo config file
repoconfig(ccdest, osdest)

# install rpms
pkgs = [ 'stack-command', 'foundation-python', 'stack-pylib',
	'foundation-python-xml', 'foundation-redhat', 'deltarpm', 
	'python-deltarpm', 'createrepo', 'foundation-py-wxPython',
	'stack-wizard', 'net-tools', 'foundation-py-pygtk' ]
installrpms(pkgs)

# cleanup ISO copies
subprocess.call(['rm', '-rf', ccdest, osdest])

# run stack add pallet on stacki and os iso
banner("Add pallets")
stackpath = '/opt/stack/bin/stack'
subprocess.call([stackpath,'add','pallet',cciso])
subprocess.call([stackpath,'add','pallet',osiso1])
if osiso2:
	subprocess.call([stackpath,'add','pallet',osiso2])

banner("Create Stack Distro")	
subprocess.call(['mkdir','-p','/export/stack/distributions/'])

pallets = 'pallets="{0},{1} {2},{3}"'.format(ccname, ccver, osname, osver)
palletssplit=pallets.split(" ")
a = "/opt/stack/bin/stack create distribution inplace=true {0}".format(pallets)
print a
subprocess.call([a], shell=True, cwd='/export/stack/distributions/')

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
	subprocess.call(['/opt/stack/bin/python',
		'/opt/stack/bin/boss_config.py'])
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
f = open("/etc/hosts","a")
string= attributes['Kickstart_PublicAddress']+"\t"+attributes['Kickstart_PrivateHostname']+"\n"
f.write(string)
f.close()
	
banner("Generate XML")
# run stack list node xml server attrs="<python dict>"
f = open("/tmp/stack.xml", "w")
subprocess.call([stackpath,'list','node','xml','server',
		'attrs={0}'.format(repr(attributes))], stdout=f)
f.close()
	
banner("Process XML")
# pipe that output to stack run pallet and output run.sh
infile = open("/tmp/stack.xml", "r")
outfile = open("/tmp/run.sh", "w")
subprocess.call([stackpath,'run','pallet'], stdin=infile, stdout=outfile)
infile.close()
outfile.close()

banner("Run Setup Script")
# run run.sh
subprocess.call(['sh','/tmp/run.sh'])

banner("Adding Pallets")
subprocess.call([stackpath, 'add', 'pallet', cciso])
subprocess.call([stackpath, 'add', 'pallet', osiso1])
if osiso2:
	subprocess.call([stackpath, 'add', 'pallet', osiso2])
subprocess.call([stackpath, 'enable', 'pallet', '%'])
	
# all done
banner("Done")
print "Reboot to complete process."
