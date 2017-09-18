#!/opt/stack/bin/python3 -E
#
# @copyright@
# @copyright@
#

import subprocess
import os

debug = open('/tmp/stacki-profile.debug', 'w')

for i in os.environ:
	debug.write('%s %s\n' % (i, os.environ[i]))	

debug.close()

#
# make sure the target directory is there
#
try:
	os.makedirs('/tmp/profile')
except:
	pass

#
# get the interfaces
#
linkcmd = [ 'ip', '-oneline', 'link', 'show' ]

p = subprocess.Popen(linkcmd, stdout = subprocess.PIPE)

interface_number = 0

curlcmd = [ '/usr/bin/curl', '--local-port', '1-100',
	'--output', '/tmp/stacki-profile.xml' ]

o, e = p.communicate()
output = o.decode()
for line in output.split('\n'):
	interface = None
	hwaddr = None

	tokens = line.split()
	if len(tokens) > 13:
		# print 'tokens: %s' % tokens
		#
		# strip off last ':'
		#
		interface = tokens[1].strip()[0:-1]

		for i in range(2, len(tokens)):
			if tokens[i] == 'link/ether':
				#
				# we know the next token is the ethernet MAC
				#
				hwaddr = tokens[i+1]
				break

		if interface and hwaddr:
			curlcmd.append('--header')
			curlcmd.append('X-RHN-Provisioning-MAC-%d: %s %s'
				% (interface_number, interface, hwaddr))

			interface_number += 1

curlcmd.append('--insecure')

#
# get the number of CPUs
#
numcpus = 0
f = open('/proc/cpuinfo', 'r')
for line in f.readlines():
	l = line.split(':')
	if l[0].strip() == 'processor':
		numcpus += 1
f.close()

server = os.environ.get('Server', None)
if not server:
	cmdline = open('/proc/cmdline', 'r')
	cmdargs = cmdline.readline()
	cmdline.close()

	for cmdarg in cmdargs.split():
		l = cmdarg.split('=')
		if l[0].strip() == 'Server':
			server = l[1]

request = 'https://%s/install/sbin/profile.cgi?os=sles&arch=x86_64&np=%d' % \
	(server, numcpus)
curlcmd.append(request)

subprocess.call(curlcmd, stdout=open('/dev/null'), stderr=open('/dev/null'))

