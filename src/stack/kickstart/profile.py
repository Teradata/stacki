#! /opt/stack/bin/python
#
# @SI_Copyright@
#                               stacki.com
#                                  v3.3
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



class Client:
        """
        Metadata for the calling client, this is always passed to
        the profile-os module to generate the installer script.
        """

        def __init__(self, **kwargs):
                self.form = cgi.FieldStorage()
                self.addr = kwargs.get('addr')
                self.port = kwargs.get('port')
                self.arch = kwargs.get('arch')
                self.np   = kwargs.get('np')
                self.os   = kwargs.get('os')

                if self.addr == None:
                        self.addr = os.environ['REMOTE_ADDR']
                if self.port == None:
                        self.port = int(os.environ['REMOTE_PORT'])

                if not self.arch:
                        try:
                                self.arch = self.form['arch'].value
                        except:
                                self.arch = None
                        if not self.arch or re.search('[^a-zA-Z0-9_]+', self.arch):
                                print("Content-type: text/html")
                                print("Status: 500 Internal Error\n")
                                print("<h1>Invalid arch field</h1>")
				self.status('install profile.cgi error (Invalid arch field)')
                                sys.exit(1)

                if not self.np:
                        try:
                                self.np = self.form['np'].value
                        except:
                                self.np = None
                        if not self.np or re.search('[^0-9]+', self.np):
                                print("Content-type: text/html")
                                print("Status: 500 Internal Error\n")
                                print("<h1>Invalid np field</h1>")
				self.status('install profile.cgi error (Invalid np field)')
                                sys.exit(1)

                if not self.os:
                        try:
                                self.os = self.form['os'].value
                        except:
                                self.os = None
                        if not self.os:
                                print("Content-type: text/html")
                                print("Status: 500 Internal Error\n")
                                print("<h1>Invalid os field</h1>")
				self.status('install profile.cgi error (Invalid os field)')
                                sys.exit(1)

                try:
                        osModule     = __import__('profile.%s' % self.os)
                        osClass      = eval('osModule.%s.Profile' % self.os)
                        self.profile = osClass()
                except ImportError:
                        self.profile = None


        def pre(self):
                """
                Run the OS-specific pre-semaphore code.
                """
                if self.profile:
                        self.profile.pre(self)

        def main(self):
                """
                Run the OS-specific profile generator.
                """
                if self.profile:
                        self.profile.main(self)

        def post(self):
                """
                Run the OS-specific post-semaphore code.
                """
                if self.profile:
                        self.profile.post(self)
                else:
                        print("Content-type: text/html")
                        print("Status: 500 Internal Error\n")
                        print("<h1>Unsupported OS</h1>")

	def status(self, message):
		if self.interactive == 1:
			return
			
		import socket
		import json

		msg = { 'source' : self.addr, 'channel' : 'health',
			'message' : message }
		m = json.dumps(msg)

		tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		tx.sendto("%s" % m, ('10.1.19.15', 5000))
		tx.close()
        
##
## MAIN
##

mutex     = stack.lock.Mutex('/var/tmp/profile.mutex')
semaphore = stack.lock.Semaphore('/var/tmp/profile.semaphore')

if not os.environ.has_key('REMOTE_ADDR'):

        # CGI's always set this, so if it doesn't exist someone is
        # running this directly on the command line for debugging

        if len(sys.argv) == 2:
                client_os = sys.argv[1]
        else:
                client_os = 'redhat'
        client = Client(**{ 'addr' : '127.0.0.1',
                            'port' : 0,
                            'arch' : 'x86_64',
                            'os'   : client_os,
                            'np'   : '1' })

	client.interactive = 1
else:
        client = Client()
	client.interactive = 0

client.status('install profile.cgi started')

syslog.openlog('profile', syslog.LOG_PID, syslog.LOG_LOCAL0)
syslog.syslog(syslog.LOG_DEBUG, 'request %s:%s' % (client.addr, client.port))
client.pre()

# Use a semaphore to restrict the number of concurrent profile
# generators.  The first time through we set the semaphore to the
# number of CPUs (not a great guess, but reasonable).

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
	print("Status: 503 Service Busy")
	print("Retry-After: 15")
	print()
	print("<h1>Service is Busy</h1>")
	empty = True
	client.status('install profile.cgi retry')
else:
	count -= 1
	semaphore.write(count)
mutex.release()
if empty:
	sys.exit(0)

syslog.syslog(syslog.LOG_DEBUG, 'semaphore push %d' % count)

#
# set some values in the database based on the web request
#
stack.api.Call('set host attr', [ client.addr, 'attr=arch', 'value=%s' % client.arch ])
stack.api.Call('set host cpus', [ client.addr, 'cpus=%s' % client.np ])

#
# add all the detected network interfaces to the database
#
ifaces = []
macs = []
modules = []
flags = []

for i in os.environ:
	if re.match('HTTP_X_RHN_PROVISIONING_MAC_[0-9]+', i):
		devinfo = os.environ[i].split()
		iface   = devinfo[0]
		macaddr = devinfo[1].lower()
		module  = ''
		if len(devinfo) > 2:
			module = devinfo[2]

		ks = ''
		if len(devinfo) > 3:
			ks = 'ks'

		ifaces.append(iface)
		macs.append(macaddr)
		modules.append(module)
		flags.append(ks)

params = []
if len(ifaces) > 0 and len(macs) > 0:
	params.append('interface=%s' % ','.join(ifaces))
	params.append('mac=%s' % ','.join(macs))

	if len(modules) > 0:
		params.append('module=%s' % (','.join(modules)))
	if len(flags) > 0:
		params.append('flag=%s' % (','.join(flags)))

	stack.api.Call('config host interface', [ client.addr ] + params)

#
# Generate the system profile
#
client.main()
		
#
# Release resource semaphore.
#
mutex.acquire()
count = semaphore.read() + 1
semaphore.write(count)
mutex.release()
syslog.syslog(syslog.LOG_DEBUG, 'semaphore pop %d' % count)
client.post()
client.status('install profile.cgi profile sent')
