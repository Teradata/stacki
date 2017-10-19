#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import sys
import string
import socket
import getopt
import stack.mq

try:
	opt, args = getopt.getopt(sys.argv[1:], 'c:')
except getopt.GetoptError as err:
	print('usage: [-c channel] message')
	sys.exit(-1)

channel = 'alert'
for o, a in opt:
	if o == '-c':
		channel = a


tx  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
pkt = '%s %s' % (channel, string.join(args))

tx.sendto(pkt, ('localhost', stack.mq.ports.publish))


