#! @PYTHON@
#
# $Id$
# 
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.15  2010/09/07 23:52:48  bruno
# star power for gb
#
# Revision 1.14  2009/06/18 04:25:00  bruno
# for anoop. he owes me *at least* a couple beers.
#
# Revision 1.13  2009/05/01 19:06:50  mjk
# chimi con queso
#
# Revision 1.12  2008/10/18 00:55:47  mjk
# copyright 5.1
#
# Revision 1.11  2008/03/06 23:41:32  mjk
# copyright storm on
#
# Revision 1.10  2007/06/23 04:03:19  mjk
# mars hill copyright
#
# Revision 1.9  2007/06/14 16:01:43  bruno
# in ananconda 10.1.1.63, when running ekv on the frontend (for a remote
# reinstall), the environment doesn't map 'localhost' to 127.0.0.1 -- so
# let's explicitly tunnel to 127.0.0.1 instead of localhost.
#
# Revision 1.8  2006/09/11 22:47:02  mjk
# monkey face copyright
#
# Revision 1.7  2006/08/10 00:09:25  mjk
# 4.2 copyright
#
# Revision 1.6  2006/08/09 15:41:38  anoop
# Changes to shootnode and rocks-console. These changes were necessary to
# support shooting multiple nodes in one command. The threading in shoot-node
# would cause a lot of problems because multiple threads would try to manipulate
# stderr, and all would fail but one.
#
# Also race conditions are created by the presence of threads, and so sockets need
# to be released only at the last possible moment, to avoid multiple bindings.
#
# Revision 1.5  2006/07/10 22:40:40  anoop
# Silly little bug removed.
#
# Revision 1.4  2006/07/03 22:13:11  anoop
# Rocks console can connect to multiple servers now without barfing
#
# Revision 1.3  2006/06/16 21:09:01  bruno
# make default local port for ekv to be 8000
#
# Revision 1.2  2006/06/15 23:04:51  bruno
# name the vncviewer window to the same name as the node it is connected to
#
# Revision 1.1  2006/06/15 21:28:47  bruno
# new command to get the vnc and ekv consoles on an installing node
#
#
#

from __future__ import print_function
import os
import sys
import stack.app
import socket
import time
import popen2
		        
class App(stack.app.Application):

	def __init__(self, argv):
		stack.app.Application.__init__(self, argv)	

		self.usage_name = 'Stacki Console'
		self.usage_version = '@VERSION@'

		self.nodename = ''
		self.known_hosts = '/tmp/.known_hosts'
		self.defaultport = 5900
		self.localport = 0
		self.remoteport = 0
		self.ekv = 0

		porthelp = '(port number of VNC server - default = %d)' \
			% (self.defaultport)


		self.getopt.l.extend([
				'ekv',
				('port=', porthelp)
			])

		return


	def parseArg(self, c):
		stack.app.Application.parseArg(self, c)

		key, val = c
		if key in ('--port'):
			self.localport = int(val)
		elif key in ('--ekv'):
			self.ekv = 1

		return


	def usageTail(self):
		return ' <nodename (e.g., backend-0-0)>\n'


	def ekvviewer(self):
		cmd = 'telnet localhost %d' % (self.localport)
		os.system(cmd)
		return


	def vncviewer(self):
		cmd = 'vncviewer --name=%s localhost:%d' \
			% (self.nodename, self.localport - self.defaultport)
		os.system(cmd)

		return

	def createSecureTunnel(self):
		#
		# use a temporary file to store the host key. we do this
		# because a new temporary host key is created in the
		# installer and if we add this temporary host key to
		# /root/.ssh/known_hosts, then the next time the node is
		# installed, the ssh tunnel will get a 'man-in-middle' error
		# and not allow port forwarding.
		#
		self.known_hosts = "%s_%s" % (self.known_hosts,self.nodename)
		if os.path.exists(self.known_hosts):
			os.unlink(self.known_hosts)

		cmd = 'ssh -q -f -o UserKnownHostsFile=%s ' % (self.known_hosts)
		cmd += '-L %d:127.0.0.1:%d ' % (self.localport, self.remoteport)
		cmd += '%s -p 2200 ' % (self.nodename)
		cmd += '\'/bin/bash -c "sleep 20"\' '
		self.s.close()
		os.system(cmd)

	def run(self):
		if len(self.args) > 0:
			self.nodename = self.args[0]
		else:
			print('\n\t"nodename" was not specified\n')
			self.usage()
			sys.exit(-1)

		self.nodename = self.args[0]

		if self.ekv == 1:
			if self.localport == 0:
				self.localport = 8000
			self.remoteport = 8000
		else:
			if self.localport == 0:
				self.localport = self.defaultport
			self.remoteport = self.defaultport

		# Check ports to see which one is open. If ports are already bound
		# go to the next one to check. Whatever binds is successfully is used.
		self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		done = 0
		while(done == 0):
		 	try:
				self.s.bind(("localhost",self.localport))
				done = 1
			except socket.error,(errno,string):
			   if(errno == 98):
				done = 0
				self.localport = self.localport + 1
		
		#Connect to the secure tunnel and go...
		self.createSecureTunnel()

		if self.ekv == 1:
			self.ekvviewer()
		else:
			self.vncviewer()

		return


app = App(sys.argv)
app.parseArgs()
app.run()

