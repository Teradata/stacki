#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

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


if 'STACKDEBUG' not in os.environ:
	lock = lockfile.pidlockfile.PIDLockFile('/var/run/%s/%s.pid' % 
			('rmq-processor', 'rmq-processor'))
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
	except:
		continue
	processor.setDaemon(True)
	processor.start()

signal.signal(signal.SIGINT, Handler)
signal.pause()
