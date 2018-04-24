#!/opt/stack/bin/python3 -E
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import subprocess
import sys

sys.path.append('/tmp')
from stack_site import *

#
# get the interfaces
#
linkcmd = [ 'ip', '-oneline', 'link', 'show' ]

p = subprocess.Popen(linkcmd, stdout = subprocess.PIPE)

interface_number = 0

curlcmd = [ '/usr/bin/curl', '--local-port', '1-100',
	'--output', '/tmp/stacki-profile.xml', '--insecure' ]

o, e = p.communicate()
for line in o.decode('utf-8').split('\n'):
	interface = None
	hwaddr = None
	tokens = line.split()

	if len(tokens) > 16:
		# print 'tokens: %s' % tokens
		#
		# strip off last ':'
		#
		# if we look for link/ we'll get all
		# interfaces, include IB, but get rid
		# of the loopback

		interface = tokens[1].strip()[0:-1]
		if interface == 'lo':
			continue

		for i in range(2, len(tokens)):
			if 'link/' in tokens[i]:
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

#
# get the make/model of the installing server
#
p = subprocess.Popen([ '/usr/sbin/dmidecode', '-s', 'system-manufacturer' ],
	stdout=subprocess.PIPE, stderr=subprocess.PIPE)
o, e = p.communicate()
try:
	curlcmd.append('--header')
	curlcmd.append('X-STACKI-MAKE: %s' % o.strip())
except:
	pass

p = subprocess.Popen([ '/usr/sbin/dmidecode', '-s', 'system-product-name' ],
	stdout=subprocess.PIPE, stderr=subprocess.PIPE)
o, e = p.communicate()
try:
	curlcmd.append('--header')
	curlcmd.append('X-STACKI-MODEL: %s' % o.strip())
except:
	pass

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

querystring = [ 'os=redhat', 'arch=x86_64', 'np=%d' % numcpus ]
server = attributes['Kickstart_PrivateAddress']

request = 'https://%s/install/sbin/profile.cgi?%s' % (server, '&'.join(querystring))
curlcmd.append(request)

subprocess.call(curlcmd, stdout=open('/dev/null'), stderr=open('/dev/null'))
