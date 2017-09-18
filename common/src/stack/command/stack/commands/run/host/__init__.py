# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


import os
import stack.commands
from stack.exception import ParamType, ParamValue


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
		if n is None:
			self.numthreads = 0
		else:
			try:
				self.numthreads = int(n)
			except:
				raise ParamType(self, 'threads', 'integer')
			if self.numthreads < 0:
				raise ParamValue(self, 'threads', '> 0')

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
		if method is None:
			method = 'ssh'

		# Check if we should collate the output
		self.collate = self.str2bool(collate)

		if self.collate:
			self.beginOutput()

		self.runImplementation(method, [self.hosts, cmd])

		if self.collate:
			self.endOutput(header=['host', 'output'], trimOwner=False)
