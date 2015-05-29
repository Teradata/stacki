# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
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

class Parallel(threading.Thread):
	def __init__(self, cmdclass, cmd, host, collate):
		threading.Thread.__init__(self)
		self.cmd = cmd
		self.host = host
		self.collate = collate
		self.cmdclass = cmdclass
		self.rc = False

	def run(self):
		(self.rc, out, err) = self.cmdclass.runHostCommand(self.host, self.cmd)

		for line in out:
			if self.collate:
				self.cmdclass.addOutput(self.host, line.strip())
			else:
				sys.stdout.write("%s\n" % line.strip())

		for line in err:
			if self.collate:
				self.cmdclass.addOutput(self.host, line.strip())
			else:
				sys.stderr.write("%s\n" % line.strip())


	
class command(stack.commands.HostArgumentProcessor,
	stack.commands.run.command):

	MustBeRoot = 0

	
class Command(command):
	"""
	Run a command for each specified host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, the command
	is run on all 'managed' hosts. By default, all compute nodes are
	'managed' nodes. To determine if a host is managed, execute:
	'rocks list host attr hostname | grep managed'. If you see output like:
	'compute-0-0: managed true', then the host is managed.
	</arg>

	<arg type='string' name='command'>
	The command to run on the list of hosts.
	</arg>

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

	<param type='string' name='num-threads'>
	The number of threads to start in parallel. If num-threads is 0, then
	try to run the command in parallel on all hosts. Default is '128'.
	</param>

	<param type='string' name='command'>
	Can be used in place of the 'command' argument.
	</param>

	<example cmd='run host compute-0-0 command="hostname"'>
	Run the command 'hostname' on compute-0-0.
	</example>

	<example cmd='run host compute "ls /tmp"'>
	Run the command 'ls /tmp/' on all compute nodes.
	</example>
	"""


	def runHostCommand(self, host, command):
		"""
		Runs the COMMAND on the remote HOST.  If the HOST is the
		current machine just run the COMMAND in a subprocess.
		"""
		
		online = True

		if host != socket.gethostname().split('.')[0]:
			# First check to make the machine is up and SSH is responding.
			#
			# This catches the case when the node is up, sshd is sitting 
			# on port 22, but it is not responding (e.g., the node is 
			# overloaded, sshd is hung, etc.)
			#
			# sock.recv() should return something like:
			#
			#	SSH-2.0-OpenSSH_4.3

			sock   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(2.0)
			try:
				sock.connect((host, 22))
				buf = sock.recv(64)
			except:
				online = False

		if online:
			proc = subprocess.Popen([ 'ssh', host, command ],
						stdin = None,
						stdout = subprocess.PIPE,
						stderr = subprocess.PIPE)

			retval = proc.wait()
			o, e   = proc.communicate()
			return (retval, o.split('\n')[:-1], e.split('\n')[:-1])

		return (None, [ 'down' ], [])




	def run(self, params, args):
		(args, command) = self.fillPositionalArgs(('command', ))

		if not command:
			self.abort('must supply a command')

		(managed, x11, t, d, c, n) = \
			self.fillParams([
				('managed', 'y'),
				('x11', 'n'),
				('timeout', '30'),
				('delay', '0'),
				('collate', 'y'),
				('num-threads', '128')
			])

		try:
			timeout = int(t)
		except:
			self.abort('"timeout" must be an integer')

		if timeout < 0:
			self.abort('"timeout" must be a postive integer')

		try:
			numthreads = int(n)
		except:
			self.abort('"num-threads" must be an integer')

		try:
			delay = float(d)
		except:
			self.abort('"delay" must be a floating point number')

		hosts = self.getHostnames(args, self.str2bool(managed))
		
		# This is the same as doing -x using ssh.  Might be useful
		# for the common case, but required for the Viz Roll.

		if not self.str2bool(x11):
			try:
				del os.environ['DISPLAY']
			except KeyError:
				pass

		# By default collate is true, unless otherwise specified
		collate = self.str2bool(c)
			
		if collate:
			self.beginOutput()

		if numthreads <= 0:
			numthreads = len(hosts)

		threads = []

		i = 0
		rc = True
		work = len(hosts)
		while work:
			
			# Run the first batch of threads

			while i < numthreads and i < len(hosts):
				host = hosts[i]
				i += 1	

				p = Parallel(self, command, host, collate)
				p.setDaemon(True)
				p.start()
				threads.append(p)

				if delay > 0:
					time.sleep(delay)

			# Collect completed threads

			try:
				totaltime = time.time()
				while timeout == 0 or (time.time() - totaltime) < timeout:

					active = threading.enumerate()

					t = threads
					for thread in t:
						if thread not in active:
							thread.join(0.1)
							threads.remove(thread)
							numthreads += 1
							work -= 1

					if len(active) == 1:
						break
				
					# don't burn a CPU while waiting for the
					# threads to complete

					time.sleep(0.5)

			except KeyboardInterrupt:
				work = 0

		if collate:
			self.endOutput(padChar='', trimOwner=False)

		for thread in threads:
			if not thread.rc:
				rc = False
				break
		return rc
