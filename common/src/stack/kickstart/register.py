#! /opt/stack/bin/python3
#
# @copyright@
# @copyright@

import os
import re
import cgi
import sys
import syslog
import stack.api
from stack.bool import *


def Lookup(key, pattern=None):
	form  = cgi.FieldStorage()
	value = form[key].value

	if pattern:
		if re.search(pattern, field):
		    print('Content-type: text/html')
		    print('Status: 500 Internal Error\n')
		    print('<h1>Invalid field %s</h1>' % field)
		    sys.exit(0)

	return value


client   = os.environ['REMOTE_ADDR']
port     = int(os.environ['REMOTE_PORT'])
ami      = Lookup('ami')
zone     = Lookup('zone')
instance = Lookup('instance')
hostname = Lookup('hostname')
box      = Lookup('box')
ip       = Lookup('ip')
mac      = Lookup('mac')

if not stack.api.Call('list host', [ hostname ]):
	stack.api.Call('add host', [ hostname, 
				     'appliance=backend',
				     'rack=%s' % zone,
				     'rank=%s' % instance,
				     'box=%s'  % box ])

	stack.api.Call('set host attr', [ hostname, 'attr=aws',      'value=true' ])
	stack.api.Call('set host attr', [ hostname, 'attr=nukedisk', 'value=true' ])

	stack.api.Call('add host interface', [ hostname, 
					       'ip=%s'  % ip, 
					       'mac=%s' % mac,
					       'interface=eth0',
					       'network=private',
					       'default=true'])

report = [ ]
for row in stack.api.Call('list host', [ hostname ]):
	boot_os     = row['os']
	boot_action = row['installaction']

for row in stack.api.Call('list bootaction', [ 'type=install',
					       'os=%s' % boot_os,
					       boot_action ]):
	kernel  = row['kernel']
	ramdisk = row['ramdisk']
	args    = row['args']
					       


report = [ ]
report.append('default=0')
report.append('timeout=0')
report.append('hiddenmenu')
report.append('title Stacki Client Install')
report.append('\troot (hd0,0)')
report.append('\tkernel /boot/%s root=LABEL=/ console=tty1 console=ttyS0 selinux=0 nvme_core.io_timeout=4294967295 %s' % (kernel, args))
report.append('\tinitrd /boot/%s' % ramdisk)


if report:
	out = '\n'.join(report)
	print('Content-type: application/octet-stream')
	print('Content-length: %d' % len(out))
	print('')
	print(out)
		
