#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import socket
import sched
import time
import os
import daemon
import lockfile.pidlockfile
import stack.mq
import stack.mq.producers

modules = []
for file in os.listdir(stack.mq.producers.__path__[0]):
	if os.path.splitext(file)[1] not in [ '.py', '.pyc']:
		continue

	module = os.path.splitext(file)[0]
	if not module or module == '__init__':
		continue

	module = 'stack.mq.producers.%s' % os.path.splitext(file)[0]
	if module not in modules:
		modules.append(module)

if 'STACKDEBUG' not in os.environ:
	lock = lockfile.pidlockfile.PIDLockFile('/var/run/%s/%s.pid' % 
			('rmq-producer', 'rmq-producer'))
	daemon.DaemonContext(pidfile=lock).open()


tx	= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
scheduler = sched.scheduler(time.time, time.sleep)
producers = []

for module in modules:
	__import__(module)
	m = eval(module)
	try:
		o = getattr(m, 'Producer')(scheduler, tx)
	except AttributeError:
		continue
	producers.append(o)

for producer in producers:
	scheduler.enter(0, 0, producer.run, ())

scheduler.run()
