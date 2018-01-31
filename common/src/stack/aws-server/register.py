#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import cgi
import json
import stack.api


def Lookup(key):
	try:
		form  = cgi.FieldStorage()
		value = form[key].value
	except:
		value = None
	return value


client	     = os.environ['REMOTE_ADDR']
port	     = int(os.environ['REMOTE_PORT'])
ami	     = Lookup('ami')
zone	     = Lookup('zone')
instance     = Lookup('instance')
hostname     = Lookup('hostname')
appliance    = Lookup('appliance')
box	     = Lookup('box')
ip	     = Lookup('ip')
mac	     = Lookup('mac')
prevHostname = None

for row in stack.api.Call('list host', [ ]):
	if instance == row['rank']:
		prevHostname = row['host']

if not prevHostname:

	# This is a new registration request, so just add the host and
	# set it to install.

	stack.api.Call('add host', [ hostname, 
				     'appliance=%s' % appliance,
				     'rack=%s'	    % zone,
				     'rank=%s'	    % instance,
				     'box=%s'	    % box ])

	stack.api.Call('add host interface', [ hostname, 
					       'ip=%s'	% ip, 
					       'mac=%s' % mac,
					       'interface=eth0',
					       'network=private',
					       'default=true',
					       'options=dhcp'])

	stack.api.Call('set host attr', [ hostname, 'attr=aws',	      'value=true' ])
	stack.api.Call('set host attr', [ hostname, 'attr=firewall',  'value=false' ])
	stack.api.Call('set host boot', [ hostname, 'action=install', 'nukedisks=true' ])

else:
	# This is a subsequent registration request, so update the the
	# database to any potential new values (hostname, ip address,
	# etc)
	if prevHostname != hostname:
		stack.api.Call('set host name', [ prevHostname, 'name=%s' % hostname ])
	stack.api.Call('set host interface ip',	 [ hostname, 'interface=eth0', 'ip=%s'	% ip ])
	stack.api.Call('set host interface mac', [ hostname, 'interface=eth0', 'mac=%s' % mac ])


report = [ ]
for row in stack.api.Call('list host', [ hostname ]):
	boot_os	    = row['os']
	boot_action = row['installaction']

for row in stack.api.Call('list host boot', [ hostname ]):
	boot = row['action']

for row in stack.api.Call('list bootaction', [ 'type=install',
					       'os=%s' % boot_os,
					       boot_action ]):
	kernel	= row['kernel']
	ramdisk = row['ramdisk']

	args = [ ]
	for arg in row['args'].split():
		tokens = arg.split('=')
		if len(tokens) == 2 and tokens[0] == 'ip':
			continue # nuke centos ip=bootif arg
		args.append(arg)
	args = ' '.join(args)


			
server = None		       
for row in stack.api.Call('list host attr', [ hostname, 
					      'attr=Kickstart_PrivateKickstartHost' ]):
	server = row['value']




grub = [ ]
grub.append('default=0')
grub.append('timeout=0')
grub.append('title stacki install')
grub.append('\troot (hd0,0)')
grub.append('\tkernel /boot/%s console=ttyS0 %s' % (kernel, args))
#grub.append('\tkernel /boot/%s %s' % (kernel, args))
grub.append('\tinitrd /boot/%s' % ramdisk)

grub2 = [ ]
grub2.append('menuentry "stacki install" {')
grub2.append('\tset root="hd0,gpt1"')
grub2.append('\tlinux  /boot/%s console=ttyS0 %s' % (kernel, args))
grub2.append('\tinitrd /boot/%s' % ramdisk)
grub2.append('}')

instructions = { }
instructions['grub']	   = '\n'.join(grub)
instructions['grub2']	   = '\n'.join(grub2)
instructions['images_url'] = 'http://%s/install/images' % server
instructions['kernel']	   = kernel
instructions['ramdisk']	   = ramdisk
instructions['boot']	   = boot
instructions['reboot']	   = boot == 'install'

out = json.dumps(instructions)
print('Content-type: application/octet-stream')
print('Content-length: %d' % len(out))
print('')
print(out)
		
