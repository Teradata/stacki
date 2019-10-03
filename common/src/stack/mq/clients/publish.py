#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import sys
import socket
import getopt
import json
import stack.mq

try:
	opt, args = getopt.getopt(sys.argv[1:], 'c:h:t:')
except getopt.GetoptError as err:
	print('usage: [-c channel] [-h host] [-t ttl] message')
	sys.exit(-1)

channel = 'alert'
host    = None
ttl     = None
for o, a in opt:
	if o == '-c':
		channel = a
	if o == '-h':
		host = a
	if o == '-t':
		ttl = int(a)
			

if host is None:

	# Crazy case for when we are in the installer and need to automatically
	# figure out where to send the message.  Just make sure to call this
	# *after* the profile.xml has been processed.

	try:
		sys.path.append('/tmp')
		from stack_site import attributes
		host = attributes['Kickstart_PrivateAddress']
	except ImportError:
		host = 'localhost'

tx  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pkt = { 'channel': channel,
	'payload': ' '.join(args) }
if ttl:
	pkt['ttl'] = ttl

tx.sendto(json.dumps(pkt).encode(), (host, stack.mq.ports.publish))
tx.close()

