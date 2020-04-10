#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import argparse
import sys
import socket
import os
import daemon
import lockfile.pidlockfile
import signal
import zmq
import stack.mq
import stack.mq.processors


def Handler(signal, frame):
	sys.exit(0)


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--daemonize", help="daemonize the process", action="store_true")
args = parser.parse_args()

if args.daemonize and 'STACKDEBUG' not in os.environ:
	lock = lockfile.pidlockfile.PIDLockFile('/var/run/%s/%s.pid' % 
						('smq-processor', 'smq-processor'))
	daemon.DaemonContext(pidfile=lock).open()


modules = []
for file in os.listdir(stack.mq.processors.__path__[0]):
	if os.path.splitext(file)[1] not in [ '.py', '.pyc']:
		continue

	module = os.path.splitext(file)[0]
	if not module or module == '__init__':
		continue

	module = 'stack.mq.processors.%s' % os.path.splitext(file)[0]
	if module not in modules:
		modules.append(module)

tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
context = zmq.Context()
for module in modules:
	try:
		__import__(module)
		m = eval(module)
		processor = getattr(m, 'Processor')(context, tx)
	except ValueError:
		continue
	processor.setDaemon(True)
	processor.start()

signal.signal(signal.SIGINT, Handler)
signal.pause()
