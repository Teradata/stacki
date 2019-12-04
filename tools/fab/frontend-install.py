#!/usr/bin/python

from __future__ import print_function
import os
import sys
import subprocess
import getopt
import tempfile
import socket
import re
import struct
import json


SITE_ATTRS_TEMPLATE = """\
Info_CertificateCountry:US
Info_CertificateLocality:Solana Beach
Info_CertificateOrganization:StackIQ
Info_CertificateState:California
Info_ClusterLatlong:N32.87 W117.22
Info_FQDN:{FQDN}
Kickstart_Keyboard:us
Kickstart_Lang:en_US
Kickstart_Langsupport:en_US
Kickstart_PrivateAddress:{NETWORK_ADDRESS}
Kickstart_PrivateDNSDomain:{DOMAIN}
Kickstart_PrivateDNSServers:{DNS_SERVERS}
Kickstart_PrivateEthernet:{MAC_ADDRESS}
Kickstart_PrivateGateway:{GATEWAY}
Kickstart_PrivateHostname:{HOSTNAME}
Kickstart_PrivateInterface:{NETWORK_INTERFACE}
Kickstart_PrivateKickstartHost:{NETWORK_ADDRESS}
Kickstart_PrivateNetmask:{NETMASK}
Kickstart_PrivateNetmaskCIDR:{NETMASK_CIDR}
Kickstart_PrivateNetwork:{NETWORK}
Kickstart_PrivateRootPassword:{SHADOW_PASSWORD}
Kickstart_PublicNTPHost:pool.ntp.org
Kickstart_Timezone:{TIMEZONE}
nukedisks:False
"""

ROLLS_XML_TEMPLATE = """\
<rolls>
	<roll arch="x86_64" diskid="{3}" name="{0}" release="{2}" url="http://127.0.0.1/mnt/cdrom/" version="{1}" />
</rolls>
"""


def banner(message):
	print('#######################################')
	print(message)
	print('#######################################')


def mount(source, dest):
	subprocess.call(['mkdir', '-p', dest])
	mnt_cmd = ['mount', '-o', 'loop,ro', source, dest]
	proc = subprocess.Popen(mnt_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	result = proc.communicate()
	if proc.returncode != 0:
		print(' '.join(mnt_cmd) + ' failed:\n' + result[0])
		proc = subprocess.Popen('mount | grep iso', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		print('mount | grep iso: \n' + proc.communicate()[0])


def umount(dest):
	subprocess.call(['umount', dest])


def installrpms(pkgs):
	if osname == 'redhat':
		cmd = [ 'yum', '-y', 'install' ]
	elif osname == 'sles':
		cmd = [ 'zypper', 'install', '-y', '-f' ]
	cmd += pkgs
	return subprocess.call(cmd)


def find_repos(iso, stacki_only=False):
	''' supports jumbo pallets as well as not blowing up on stackios '''

	mountdir = os.path.join('/run', os.path.basename(iso))

	mount(iso, mountdir)

	repodirs = []

	search_dir = mountdir
	if stacki_only:
		# if stacki_only, go straight to that directory
		search_dir = os.path.join(mountdir, 'stacki')

	for (path, dirs, files) in os.walk(search_dir):
		if 'suse' in dirs:
			repodirs.append(os.path.join(path, 'suse'))
		elif 'repodata' in dirs:
			repodirs.append(path)

#	umount(mountdir)
	return repodirs


def repoconfig(stacki_iso, extra_isos):
	# we only want to pull stacki from 'stacki_iso'
	# but we'll look for all pallets in 'extra_isos'

	if extra_isos:
		#
		# we are going to use the ISO(s) described in the 'extra_isos'
		# list, so let's move the CentOS repo files out of the way.
		#
		if osname == 'redhat':
			repodir = '/etc/yum.repos.d'
		elif osname == 'sles':
			repodir = '/etc/zypp/repos.d'

		subprocess.call(['mkdir', '-p', '%s/save' % repodir])

		files = os.listdir(repodir)
		for f in files:
			if os.path.isfile('%s/%s' % (repodir, f)):
				subprocess.call(['mv', '%s/%s' % (repodir, f),
					'%s/save/' % repodir])

	count = 0
	repos = find_repos(stacki_iso, stacki_only=True)
	for iso in extra_isos:
		repos.extend(find_repos(iso))

	if osname == 'redhat':
		with open('/etc/yum.repos.d/stacki.repo', 'w') as repofile:
			for repo in repos:
				count += 1
				reponame = "iso_repo_%s" % count
				repofile.write('[%s]\n' % reponame)
				repofile.write('name=%s\n' % reponame)
				repofile.write('baseurl=file://%s\n' % (repo))
				repofile.write('assumeyes=1\n')
				repofile.write('gpgcheck=no\n\n')
	elif osname == 'sles':
		with open('/etc/zypp/repos.d/stacki.repo', 'w') as repofile:
			for repo in repos:
				count += 1
				reponame = "iso_repo_%s" % count
				repofile.write('[%s]\n' % reponame)
				repofile.write('name=%s\n' % reponame)
				repofile.write('baseurl=file://%s\n' % (repo))
				repofile.write('assumeyes=1\n')
				repofile.write('gpgcheck=no\n\n')

	#
	# clean/initialize the repos
	#
	if osname == 'redhat':
		cmd = [ 'yum', 'clean', 'all' ]
	elif osname == 'sles':
		cmd = [ 'zypper', 'clean', '--all' ]
	return subprocess.call(cmd)


def ldconf():
	file = open('/etc/ld.so.conf.d/foundation.conf', 'w')
	file.write('/opt/stack/lib\n')
	file.close()

	subprocess.call(['ldconfig'])


def usage():
	print("Required arguments:")
	print("\t--stacki-iso=ISO : path to stacki ISO")
	print("Optional arguments:")
	print("\t--extra-iso=iso1,iso2,iso3.. : list of pallets to add")
	print("\t--use-existing : use the existing system settings and root password")

#
# MAIN
#

#
# log all output to a file too
#
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

tee = subprocess.Popen(["tee", "/tmp/frontend-install.log"],
	stdin=subprocess.PIPE)
os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
os.dup2(tee.stdin.fileno(), sys.stderr.fileno())

#
# determine if this is CentOS/RedHat or SLES
#
if os.path.exists('/etc/redhat-release'):
	osname = 'redhat'
elif os.path.exists('/etc/SuSE-release'):
	osname = 'sles'
else:
	print('Unrecognized operating system\n')
	usage()
	sys.exit(-1)

#
# process the command line arguments
#
opts, args = getopt.getopt(
	sys.argv[1:],
	'',
	['stacki-iso=', 'extra-iso=', 'use-existing']
)

stacki_iso = None
extra_isos = []
use_existing = False

for opt, arg in opts:
	if opt == '--stacki-iso':
		stacki_iso = arg
	elif opt == '--extra-iso':
		extra_isos = arg.split(',')
	elif opt == '--use-existing':
		use_existing = True

if not stacki_iso:
	print('--stacki-iso is not specified\n')
	usage()
	sys.exit(-1)

if not os.path.exists(stacki_iso):
	print("Error: File '{0}' does not exist.".format(stacki_iso))
	sys.exit(1)

for iso in extra_isos:
	if not os.path.exists(iso):
		print("Error: File '{0}' does not exist.".format(iso))
		sys.exit(1)

banner("Bootstrap Stack Command Line")

# turn off NetworkManager so it doesn't overwrite our networking info
subprocess.call(['service', 'NetworkManager', 'stop'])

stacki_iso = os.path.abspath(stacki_iso)

mount(stacki_iso, os.path.join('/run', os.path.basename(stacki_iso)))
for iso in extra_isos:
	iso_path = os.path.abspath(iso)
	mount(iso, os.path.join('/run', os.path.basename(iso)))

# create repo config file
repoconfig(stacki_iso, extra_isos)

pkgs = [
	'foundation-python',
	'foundation-python-PyMySQL',
	'stack-command',
	'stack-pylib',
	'stack-mq',
	'net-tools',
	'foundation-newt',
	'stack-wizard',
	'rsync',
	'stack-kickstart',
]

if osname == 'redhat':
	pkgs.append('foundation-redhat')

# Workaround to add new packages but not break this script for older stacki releases
new_pkgs = [
	'stack-templates',
	'stack-probepal',
]

for new_pkg in new_pkgs:
	if osname == 'redhat' and subprocess.call(['yum', 'info', new_pkg]) == 0:
		pkgs.append(new_pkg)
	elif osname == 'sles' and "not found" not in str(subprocess.check_output(['zypper', 'info', new_pkg])):
		pkgs.append(new_pkg)

return_code = installrpms(pkgs)

if return_code != 0:
	print("Error: stacki package installation failed")
	sys.exit(return_code)


banner("Configuring dynamic linker for stacki")
ldconf()

if not os.path.exists('/tmp/site.attrs') and not os.path.exists('/tmp/rolls.xml'):
	if use_existing:
		# Construct site.attrs and rolls.xml from the exising system
		banner("Pulling existing info")
		attrs = {}

		# Get our FQDN and split it into its parts
		attrs['FQDN'] = socket.getfqdn()
		fqdn = attrs['FQDN'].split('.')
		attrs['HOSTNAME'] = fqdn.pop(0)
		attrs['DOMAIN'] = '.'.join(fqdn)

                # Reject frontend and backend as hostnames
		if attrs['HOSTNAME'].lower() in ['frontend', 'backend']:
			print('Cannot have an appliance name as a hostname')
			sys.exit(1)

		# Figure out which interface to use
		interfaces = []
		for line in subprocess.check_output("ip -o -4 address", shell=True).splitlines():
			interface = re.match(r'\d+:\s+(\S+)\s+', line).group(1)
			if interface != 'lo':
				interfaces.append((interface, line))

		if len(interfaces) == 0:
			print("Error: No interfaces found.")
			sys.exit(1)

		interface = interfaces[0]
		if len(interfaces) > 1:
			print("\nI found more than one interface, which one do you want to use?\n")
			for ndx, interface in enumerate(interfaces):
				print("  {}) {} {}".format(
					ndx + 1,
					interface[0],
					re.search(r'inet\s+([\d.]+)/', interface[1]).group(1)
				))

			# Make input work on both python 2 and 3
			try:
				get_input = raw_input
			except NameError:
				get_input = input

			for _ in range(3):
				try:
					choice = int(get_input("\nType the interface number: ")) - 1
					interface = interfaces[choice]
					break
				except:
					print("\nError: Bad choice, Try again.")
			else:
				print("\nError: Failed after 3 tries.")
				sys.exit(1)

		# Pull in the interface info
		attrs['NETWORK_INTERFACE'] = interface[0]
		match = re.match(r'\d+:\s+\S+\s+inet\s+([\d.]+)/(\d+)\s+brd\s+([\d.]+)', interface[1])
		if match:
			attrs['NETWORK_ADDRESS'] = match.group(1)
			attrs['NETMASK_CIDR'] = int(match.group(2))
			attrs['BROADCAST_ADDRESS'] = match.group(3)
		else:
			print("Error: Network info not found.")
			sys.exit(1)

		# Calculate the NETMASK. Start with 32 bits on, shift zeros for the CIDR length,
		# then slice it back to 32 bits
		netmask = (0xFFFFFFFF << (32 - attrs['NETMASK_CIDR'])) & 0xFFFFFFFF
		attrs['NETMASK'] = socket.inet_ntoa(struct.pack('!I', netmask))

		# Calculate the NETWORK address based on the netmask
		inet_address = struct.unpack('!I', socket.inet_aton(attrs['NETWORK_ADDRESS']))[0]
		network_address = inet_address & netmask
		attrs['NETWORK'] = socket.inet_ntoa(struct.pack('!I', network_address))

		# Get the MAC_ADDRESS
		for line in subprocess.check_output("ip -o link", shell=True).splitlines():
			if line.split(':')[1].strip() == interface[0]:
				attrs['MAC_ADDRESS'] = re.search(r'link/ether\s+([0-9a-f:]{17})\s+', line).group(1)
				break
		else:
			print("Error: MAC address not found.")
			sys.exit(1)

		# Get the GATEWAY
		gateways = []
		for line in subprocess.check_output("ip route", shell=True).splitlines():
			parts = line.split()
			if parts[0] == 'default':
				gateways.append((parts[4], parts[2]))

		if len(gateways) == 0:
			print("Error: Network gateway not found.")
			sys.exit(1)

		gateway = gateways[0][1]
		if len(gateways) > 1:
			print("\nI found more than one default gateway, which one do you want to use?\n")
			for ndx, gateway in enumerate(gateways):
				print("  {}) {} {}".format(
					ndx + 1,
					gateway[0],
					gateway[1]
				))

			# Make input work on both python 2 and 3
			try:
				get_input = raw_input
			except NameError:
				get_input = input

			for _ in range(3):
				try:
					choice = int(get_input("\nType the gateway number: ")) - 1
					gateway = gateways[choice][1]
					break
				except:
					print("\nError: Bad choice, Try again.")
			else:
				print("\nError: Failed after 3 tries.")
				sys.exit(1)

		attrs['GATEWAY'] = gateway

		# Get the DNS_SERVERS
		dns_servers = []
		for line in open('/etc/resolv.conf'):
			if 'nameserver' in line:
				dns_servers.append(line.split()[1])

		if len(dns_servers):
			attrs['DNS_SERVERS'] = ','.join(dns_servers)
		else:
			print("Error: DNS server not found.")
			sys.exit(1)

		# Get the timezone from the /etc/localtime symlink
		path = os.path.realpath('/etc/localtime')
		if path.startswith('/usr/share/zoneinfo/'):
			attrs['TIMEZONE'] = path[20:]
		else:
			print("Error: Timezone not found.")
			sys.exit(1)

		# Steal the root shadow password
		for line in open('/etc/shadow'):
			if line.startswith('root:'):
				attrs['SHADOW_PASSWORD'] = line.split(':')[1]
				break
		else:
			print("Error: Shadow password not found.")
			sys.exit(1)

		# Write out site.attrs
		with open('/tmp/site.attrs', 'w') as f:
			f.write(SITE_ATTRS_TEMPLATE.format(**attrs))

		# Use the stacki version of python3 and run the wizard code
		# to get the pallet info from the mounted ISO
		mount(stacki_iso, '/mnt/cdrom')

		roll_info = json.loads(subprocess.check_output([
			'/opt/stack/bin/python3',
			'-c',
			'from stack.wizard import Data;'
			'import json;'
			'print(json.dumps(Data().getDVDPallets()[0]))'
		]))

		umount('/mnt/cdrom')

		# Write out rolls.xml
		with open('/tmp/rolls.xml', 'w') as f:
			f.write(ROLLS_XML_TEMPLATE.format(*roll_info))

	else:
		#
		# execute boss_config.py. completing this wizard creates
		# /tmp/site.attrs and /tmp/rolls.xml
		#
		banner("Launch Boss-Config")
		mount(stacki_iso, '/mnt/cdrom')

		subprocess.call([
			'/opt/stack/bin/python3',
			'/opt/stack/bin/boss_config_snack.py',
			'--no-partition',
			'--no-net-reconfig'
		])

		umount('/mnt/cdrom')

	# add missing attrs to site.attrs
	with open("/tmp/site.attrs", "a") as attrs_file:
		attrs_file.write("Server_Partitioning:force-default-root-disk-only\n")

# convert site.attrs to python dict
f = [line.strip() for line in open("/tmp/site.attrs", "r")]
attributes = {"barnacle": "True"}
for line in f:
	split = line.split(":", 1)
	attributes[split[0]] = split[1]

# Reject frontend and backend as hostnames
hostname = attributes['Kickstart_PrivateHostname'].lower()
if hostname in ['frontend', 'backend']:
	print('Cannot have an appliance name as a hostname')
	sys.exit(1)

if not use_existing:
	# fix hostfile
	with open("/etc/hosts", "a") as f:
		f.write('{}\t{} {}\n'.format(
			attributes['Kickstart_PrivateAddress'],
			attributes['Kickstart_PrivateHostname'],
			attributes['Info_FQDN']
		))

	# set the hostname to the user-entered FQDN
	print('Setting hostname to %s' % attributes['Info_FQDN'])
	subprocess.call(['hostname', attributes['Info_FQDN']])

	# Set the root password to what the user entered
	print("Setting root password")
	subprocess.call([
		'usermod',
		'-p',
		attributes['Kickstart_PrivateRootPassword'],
		'root'
	])

stackpath = '/opt/stack/bin/stack'
subprocess.call([stackpath, 'add', 'pallet', stacki_iso])
banner("Generate XML")
# run stack list node xml server attrs="<python dict>"
f = open("/tmp/stack.xml", "w")
cmd = [ stackpath, 'list', 'node', 'xml', 'server',
	'attrs={0}'.format(repr(attributes))]
print('cmd: %s' % ' '.join(cmd))
p = subprocess.Popen(cmd, stdout=f, stderr=None)
rc = p.wait()
f.close()

if rc:
	print("Could not generate XML")
	sys.exit(rc)

banner("Process XML")
# pipe that output to stack run pallet and output run.sh
infile = open("/tmp/stack.xml", "r")
outfile = open("/tmp/run.sh", "w")
cmd = [stackpath, 'list', 'host', 'profile', 'chapter=main', 'profile=bash']
p = subprocess.Popen(cmd, stdin=infile,
	stdout=outfile)
rc = p.wait()
infile.close()
outfile.close()

if rc:
	print("Could not process XML")
	sys.exit(rc)

banner("Run Setup Script")
# run run.sh
p = subprocess.Popen(['sh', '/tmp/run.sh'])
rc = p.wait()
if rc:
	print("Setup Script Failed")
	sys.exit(rc)

banner("Adding Pallets")
subprocess.call([stackpath, 'add', 'pallet', stacki_iso])
for iso in extra_isos:
	iso = os.path.abspath(iso)
	subprocess.call([stackpath, 'add', 'pallet', iso])
subprocess.call([stackpath, 'enable', 'pallet', '%'])
subprocess.call([stackpath, 'enable', 'pallet', '%', 'box=frontend'])

subprocess.call([stackpath, 'sync', 'config'])
# all done
banner("Done")

print("Reboot to complete process.")

