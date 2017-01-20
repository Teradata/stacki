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


import threading
import os
import sys
import time
import socket
import subprocess
import shlex
import stack.commands
from stack.exception import *


class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	Run a command for each specified host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, the command
	is run on all 'managed' hosts. By default, all compute nodes are
	'managed' nodes. To determine if a host is managed, execute:
	'rocks list host attr hostname | grep managed'. If you see output like:
	'compute-0-0: managed true', then the host is managed.
	</arg>

	<param type='string' name='command' optional='0'>
	The command to run on the list of hosts.
	</param>

	<param type='boolean' name='managed'>
	Run the command only on 'managed' hosts, that is, hosts that generally
	have an ssh login. Default is 'yes'.
	</param>

	<param type='boolean' name='x11'>
	If 'yes', enable X11 forwarding when connecting to hosts.
	Default is 'no'.
	</param>

	<param type='string' name='timeout'>
	Sets the maximum length of time (in seconds) that the command is
	allowed to run.
	Default is '30'.
	</param>

	<param type='string' name='delay'>
	Sets the time (in seconds) to delay between each executed command
	on multiple hosts. For example, if the command is run on two
	hosts and if the delay is 10, then the command will be executed on host
	1, then 10 seconds later, the command will be executed on host 2.
	Default is '0' (no delay).
	</param>

	<param type='string' name='collate'>
	Prepend the hostname to every output line if this parameter is set to
	'yes'. Default is 'yes'.
	</param>

	<param type='string' name='threads'>
	The number of threads to start in parallel. Default is 0.
	Set "run.host.threads" to set the default
	</param>

	<example cmd='run host backend-0-0 command="hostname"'>
	Run the command 'hostname' on backend-0-0.
	</example>

	<example cmd='run host backend command="ls /tmp"'>
	Run the command 'ls /tmp/' on all backend nodes.
	</example>
	"""

	def run(self, params, args):

		# Parse Params
		(cmd, managed, x11, t, d, collate, n, method) = self.fillParams([
                        ('command', None, True),	# Command
                        ('managed', 'y'),		# Run on Managed Hosts only
                        ('x11', 'n'),			# Run without X11
                        ('timeout', '0'),		# Set timeout for commands
			('delay', '0'),			# Set delay between each thread
			('collate', 'y'),		# Collate output
			('threads', self.getAttr('run.host.threads')),
			('method', self.getAttr('run.host.impl'))
			])

		# Get list of hosts to run the command on
		self.hosts = self.getHostnames(args, self.str2bool(managed))

		# Get timeout for commands
		try:
			self.timeout = int(t)
		except:
                        raise ParamType(self, 'timeout', 'integer')
		if self.timeout < 0:
                        raise ParamValue(self, 'timeout', '> 0')

		# Get Number of threads to run concurrently
		if n == None:
			self.numthreads = 0
		else:
			try:
				self.numthreads = int(n)
			except:
				raise ParamType(self, 'threads', 'integer')
			if self.numthreads < 0:
				raise ParamValue(self, 'threads','> 0')

		# Get time to pause between subsequent threads
		try:
			self.delay = float(d)
		except:	
                        raise ParamType(self, 'delay', 'float')

		# Check if we want to unset the Display
		if not self.str2bool(x11):
			try:
				del os.environ['DISPLAY']
			except KeyError:
				pass

		# Get the command
		self.cmd = cmd

		# Get the implementation to run. By default, run SSH
		if method == None:
			method = 'ssh'

		# Check if we should collate the output
		self.collate = self.str2bool(collate)

		if self.collate:
			self.beginOutput()

		self.runImplementation(method, [self.hosts, cmd])

		if self.collate:
			self.endOutput(header=['host','output'], trimOwner = False)
