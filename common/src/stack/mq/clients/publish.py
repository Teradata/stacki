#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import sys
import string
import socket
import getopt
import stack.mq
import json

try:
	opt, args = getopt.getopt(sys.argv[1:], 'c:h:')
except getopt.GetoptError as err:
	print('usage: [-c channel] [-h host] message')
	sys.exit(-1)

channel = 'alert'
host = 'localhost'
for o, a in opt:
	if o == '-c':
		channel = a
	if o == '-h':
		host = a


tx  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pkt = { "channel": channel,
	"message": ' '.join(args) }

tx.sendto(json.dumps(pkt).encode(), (host, stack.mq.ports.publish))


