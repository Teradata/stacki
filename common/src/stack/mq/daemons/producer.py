#! /opt/stack/bin/python3
#
# @SI_Copyright@
#			       stacki.com
#				  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

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
