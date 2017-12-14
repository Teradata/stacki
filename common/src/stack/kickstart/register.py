#! /opt/stack/bin/python3
#
# @copyright@
# @copyright@

import os
import re
import cgi
import sys
import json
import syslog
import stack.api
from stack.bool import *


def Lookup(key, pattern=None):
	try:
		form  = cgi.FieldStorage()
		value = form[key].value
	except:
		value = None

	if pattern:
		if re.search(pattern, field):
		    print('Content-type: text/html')
		    print('Status: 500 Internal Error\n')
		    print('<h1>Invalid field %s</h1>' % field)
		    sys.exit(0)

	return value

client	  = os.environ['REMOTE_ADDR']
port	  = int(os.environ['REMOTE_PORT'])
ami	  = Lookup('ami')
zone	  = Lookup('zone')
instance  = Lookup('instance')
hostname  = Lookup('hostname')
appliance = Lookup('appliance')
box	  = Lookup('box')
ip	  = Lookup('ip')
mac	  = Lookup('mac')

if not appliance:
	appliance = 'backend'

if not stack.api.Call('list host', [ hostname ]):
	stack.api.Call('add host', [ hostname, 
				     'appliance=%s' % appliance,
				     'rack=%s'	    % zone,
				     'rank=%s'	    % instance,
				     'box=%s'	    % box ])

	stack.api.Call('set host attr', [ hostname, 'attr=aws',	      'value=true' ])
	stack.api.Call('set host attr', [ hostname, 'attr=firewall',  'value=false' ])
	stack.api.Call('set host attr', [ hostname, 'attr=nukedisks', 'value=true' ])

	stack.api.Call('add host interface', [ hostname, 
					       'ip=%s'	% ip, 
					       'mac=%s' % mac,
					       'interface=eth0',
					       'network=private',
					       'default=true',
					       'options=dhcp'])

report = [ ]
for row in stack.api.Call('list host', [ hostname ]):
	boot_os	    = row['os']
	boot_action = row['installaction']

for row in stack.api.Call('list bootaction', [ 'type=install',
					       'os=%s' % boot_os,
					       boot_action ]):
	kernel	= row['kernel']
	ramdisk = row['ramdisk']
	args	= row['args']

			
server = None		       
for row in stack.api.Call('list host attr', [ hostname, 
					      'attr=Kickstart_PrivateKickstartHost' ]):
	server = row['value']




grub = [ ]
grub.append('default=0')
grub.append('timeout=0')
grub.append('hiddenmenu')
grub.append('title Stacki Client Install')
grub.append('\troot (hd0,0)')
grub.append('\tkernel /boot/%s root=LABEL=/ console=tty1 console=ttyS0 selinux=0 nvme_core.io_timeout=4294967295 %s' % (kernel, args))
grub.append('\tinitrd /boot/%s' % ramdisk)

instructions = { }
instructions['grub']	   = '\n'.join(grub)
instructions['images_url'] = 'http://%s/install/images' % server
instructions['kernel']	   = kernel
instructions['ramdisk']	   = ramdisk
instructions['reboot']	   = True

out = json.dumps(instructions)
print('Content-type: application/octet-stream')
print('Content-length: %d' % len(out))
print('')
print(out)
		
