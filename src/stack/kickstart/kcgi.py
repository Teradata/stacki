#! /opt/stack/bin/python
#
# @SI_Copyright@
#                             www.stacki.com
#                                  v3.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
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
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@

from __future__ import print_function
import os
import re
import fcntl
import sys
import cgi
import string
import syslog
import stack.lock
import stack.api

mutex     = stack.lock.Mutex('/var/tmp/kickstart.mutex')
semaphore = stack.lock.Semaphore('/var/tmp/kickstart.semaphore')
form      = cgi.FieldStorage()		# URL attributes
report    = []				# Output
caddr	  = os.environ['REMOTE_ADDR']
cport     = int(os.environ['REMOTE_PORT'])

syslog.openlog('kickstart', syslog.LOG_PID, syslog.LOG_LOCAL0)
syslog.syslog(syslog.LOG_DEBUG, 'request %s:%s' % (caddr, cport))

# Deny all requests that come from non-priviledged ports
# This means only a root user can request a kickstart file
		
if cport > 1023:
	print("Content-type: text/html")
	print("Status: 401 Unauthorized")
	print()
	print("<h1>Unauthorized</h1>")
	sys.exit(1)


# Require the ARCH and NP fields in the URL and sanitize
# them for use in the database.
# Loader provides these today, so we should never trigger this code.

try:
	arch = form['arch'].value
except:
	arch = None
if not arch or re.search('[^a-zA-Z0-9_]+', arch):
	print("Content-type: text/html")
	print("Status: 500 Internal Error")
	print()
	print("<h1>Invalid arch field</h1>")
	sys.exit(1)

try:
	np = form['np'].value
except:
	np = None
if not np or re.search('[^0-9]+', np):
	print("Content-type: text/html")
	print("Status: 500 Internal Error")
	print()
	print("<h1>Invalid np field</h1>")
	sys.exit(1)

        
# Use a semaphore to restrict the number of concurrent kickstart
# file generators.  The first time through we set the semaphore
# to the number of CPUs (not a great guess, but reasonable).

empty = False
mutex.acquire()
count = semaphore.read()
if count == None:
	try:
		cmd = "grep 'processor' /proc/cpuinfo | wc -l"
		out = os.popen(cmd).readline()
		count = int(out)
	except:
		count = 8
if count == 0:
	# Out of resources force the client to retry,
	# and exit the cgi after we release the mutex.
	print("Content-type: text/html")
	print( "Status: 503 Service Busy")
	print("Retry-After: 15")
	print()
	print("<h1>Service is Busy</h1>")
	empty = True
else:
	count -= 1
	semaphore.write(count)
mutex.release()

if empty:
	sys.exit(0)

syslog.syslog(syslog.LOG_DEBUG, 'semaphore push %d' % count)

stack.api.Call('set host attr', [ caddr, 'attr=arch', 'value=%s' % arch ])
stack.api.Call('set host cpus', [ caddr, 'cpus=%s' % np ])

cmd = '/opt/stack/bin/stack list host xml arch=%s os=redhat %s' % \
    (arch, caddr)
for line in os.popen(cmd).readlines():
	report.append(line[:-1])

#
# get the avalanche attributes
#

result = stack.api.Call('list host attr', [ caddr ])
attrs  = {}
for dict in result:
	if dict['attr'] in [
			'Kickstart_PrivateKickstartHost',
			'trackers',
			'pkgservers' ]:
		attrs[dict['attr']] = dict['value'] 

if not attrs.has_key('trackers'):
	attrs['trackers'] = attrs['Kickstart_PrivateKickstartHost']
if not attrs.has_key('pkgservers'):
	attrs['pkgservers'] = attrs['Kickstart_PrivateKickstartHost']

#
# Done
#
if report:
	out = string.join(report, '\n')
	print('Content-type: application/octet-stream')
	print('Content-length: %d' % (len(out)))
	print('X-Avalanche-Trackers: %s' % (attrs['trackers']))
	print('X-Avalanche-Pkg-Servers: %s' % (attrs['pkgservers']))
	print('')
	print(out)
		
#
# Release resource semaphore.
#

mutex.acquire()
count = semaphore.read() + 1
semaphore.write(count)
mutex.release()
syslog.syslog(syslog.LOG_DEBUG, 'semaphore pop %d' % count)
