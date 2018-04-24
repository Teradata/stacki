#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import re
import sys
import cgi
import syslog
import stack.lock
import stack.api
import stack.bool


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
		self.np	  = kwargs.get('np')
		self.os	  = kwargs.get('os')

		if self.addr is None:
			self.addr = os.environ['REMOTE_ADDR']
		if self.port is None:
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
			osClass	     = eval('osModule.%s.Profile' % self.os)
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
		tx.sendto(m.encode(), ('127.0.0.1', 5000))
		tx.close()
	
##
## MAIN
##


mutex	  = stack.lock.Mutex('/var/tmp/profile.mutex')
semaphore = stack.lock.Semaphore('/var/tmp/profile.semaphore')

if 'REMOTE_ADDR' not in os.environ:

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
if count is None:
	syslog.syslog(syslog.LOG_DEBUG, 'semaphore not found')
	try:
		cmd = "grep 'processor' /proc/cpuinfo | wc -l"
		out = os.popen(cmd).readline()
		count = int(out)
	except:
		count = 8
if count == 0:
	syslog.syslog(syslog.LOG_DEBUG, 'semaphore found but zero')
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
stack.api.Call('set host attr', [ client.addr, 'attr=cpus', 'value=%s' % client.np ])

#
# update the MAC info in the database
#
# but there are certain cases in which you don't want the MACs updated -- in
# that case, set the attribute 'profile.update_macs' to 'false'.
#
profile_update_macs = 1

output = stack.api.Call('list host attr',
	[ client.addr, 'attr=profile.update_macs' ])

if output:
	row = output[0]

	if not stack.bool.str2bool(row['value']):
		profile_update_macs = 0

if profile_update_macs:
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
			iface	= devinfo[0]
			macaddr = devinfo[1].lower()
			module	= ''
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

		stack.api.Call('config host interface',
			[ client.addr ] + params)

#
# add the 'make' and 'model' to the database
#
if 'HTTP_X_STACKI_MAKE' in os.environ:
	make = os.environ['HTTP_X_STACKI_MAKE']
	stack.api.Call('set host attr', [ client.addr, 'attr=component.make',
		'value="%s"' % make ])

if 'HTTP_X_STACKI_MODEL' in os.environ:
	model = os.environ['HTTP_X_STACKI_MODEL']
	stack.api.Call('set host attr', [ client.addr, 'attr=component.model',
		'value="%s"' % model ])

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
