#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import sys
import getopt
import stack.mq
import json
import zmq

try:
	opt, args = getopt.getopt(sys.argv[1:], 'c:H:',['command','host'])
except getopt.GetoptError:
	print('usage: [ -c enable | disable | status ] [ -H host ] {channel}')
	sys.exit(-1)

control = 'rmq'
command = 'enable'
host = 'localhost'

for o, a in opt:
	if o in ['-h','--help']:
		usage()
	elif o in ['-c', '--command']:
		command = a.strip()
	elif o in ['-H','--host']:
		host = a.strip()

try:
	channel = args[0].strip()
except:
	channel = control
message = {'channel': channel, 'type':'','command':command}

context = zmq.Context()
sock = context.socket(zmq.REQ)
sock.connect("tcp://%s:%d" % (host, stack.mq.ports.control))

sock.send_string(json.dumps(message))
m = sock.recv().decode()
print (m)

