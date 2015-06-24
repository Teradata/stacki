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
print sys.argv[1:]
if len(sys.argv[1:]) != 6:
	print "Requires exactly 6 arguments, in order:"
	print "\tpath to stacki ISO"
	print "\tstacki short name (usually 'stacki')"
	print "\tstacki version"
	print "\tpath to OS ISO"
	print "\tOS short name (eg 'CentOS')"
	print "\tOS version"
	exit()

cciso = sys.argv[1]
ccname = sys.argv[2]
ccver = sys.argv[3]
osiso = sys.argv[4]
osname = sys.argv[5]
osver = sys.argv[6]

if not os.path.exists(cciso):
	print "Error: File '{0}' does not exist.".format(cciso)
	exit()
if not os.path.exists(osiso):
	print "Error: File '{0}' does not exist.".format(osiso)
	exit()

banner("Boostrap Stack Command Line")

# turn off NetworkManager so it doesn't overwrite our networking info
subprocess.call(['service', 'NetworkManager', 'stop'])

# mount the isos
ccmnt = '/mnt/cdrom'
mount(cciso, ccmnt)
osmnt = '/mnt/disk2'
mount(osiso, osmnt)

# create repo config file
repoconfig(ccmnt, osmnt)

# install rpms
pkgs = [ 'stack-command', 'foundation-python', 'stack-pylib',
	'foundation-python-xml', 'foundation-redhat', 'deltarpm', 
	'python-deltarpm', 'createrepo', 'foundation-py-wxPython',
	'stack-wizard', 'net-tools' ]
installrpms(pkgs)

umount(ccmnt)
umount(osmnt)

# run stack add pallet on stacki and os iso
banner("Add pallets")
stackpath = '/opt/stack/bin/stack'
subprocess.call([stackpath,'add','pallet',cciso])
subprocess.call([stackpath,'add','pallet',osiso])

banner("Create Stack Distro")	
subprocess.call(['mkdir','-p','/export/stack/distributions/'])

pallets = 'pallets="{0},{1} {2},{3}"'.format(ccname, ccver, osname, osver)
palletssplit=pallets.split(" ")
a = "/opt/stack/bin/stack create distribution inplace=true {0}".format(pallets)
print a
subprocess.call([a], shell=True, cwd='/export/stack/distributions/')

banner("Configuring dynamic linker for stacki")
ldconf()

# execute boss_config.py.  completing this wizard drops /tmp/site.attrs
banner("Launch Boss-Config")
mount(cciso, ccmnt)
subprocess.call(['/opt/stack/bin/python','/opt/stack/bin/boss_config.py'])
umount(ccmnt)
	
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
subprocess.call([stackpath, 'add', 'pallet', osiso])
subprocess.call([stackpath, 'enable', 'pallet', '%'])
	
# all done
banner("Done")
print "Reboot to complete process."
