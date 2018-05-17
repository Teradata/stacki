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
from stack.util import get_interfaces

sys.path.append('/tmp')
from stack_site import *

#
# get the interfaces
#
interface_number = 0

curlcmd = [ '/usr/bin/curl', '--local-port', '1-100',
	'--output', '/tmp/stacki-profile.xml' ]

for interface, hwaddr in get_interfaces():
	if interface and hwaddr:
		curlcmd.append('--header')
		curlcmd.append('X-RHN-Provisioning-MAC-%d: %s %s' % (interface_number, interface, hwaddr))
		interface_number += 1
	curlcmd.append('-k')

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

server = attributes['Kickstart_PrivateAddress']

request = 'https://%s/install/sbin/profile.cgi?os=redhat&arch=x86_64&np=%d' % \
	(server, numcpus)
curlcmd.append(request)

subprocess.call(curlcmd, stdout=open('/dev/null'), stderr=open('/dev/null'))
