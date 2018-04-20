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
import stack.commands
from stack.exception import ParamType, ParamValue
import threading
import socket
import time
import subprocess

class Parallel(threading.Thread):
	def __init__(self, cmd, host, output, timeout):
		threading.Thread.__init__(self)
		self.cmd = cmd
		self.host = host
		self.output = output
		self.timeout = timeout

	def run(self):
		"""
		Runs the COMMAND on the remote HOST.  If the HOST is the
		current machine just run the COMMAND in a subprocess.
		"""

		online = True

		if self.host != socket.gethostname().split('.')[0]:
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
				sock.connect((self.host, 22))
				buf = sock.recv(64)
			except:
				online = False

		# If we're online, run the SSH command. Make sure to
		# pipe STDERR to STDOUT. We wan't to merge the streams
		# as if this were the output of running the command on
		# the command line.
		if online:
			proc = subprocess.Popen([ 'ssh', self.host, self.cmd ],
						stdin=None,
						stdout=subprocess.PIPE,
						stderr=subprocess.STDOUT)

			# If we dont have a timeout, just wait for the process
			# to finish
			if self.timeout <= 0:
				retval = proc.wait()
			else:
				hit_timeout = False
				start_time = time.time()
				while hit_timeout is False:
					# Check if process is done
					retval = proc.poll()
					if retval is not None:
						break
					# If we're not done, check if we're out
					# of time.
					if time.time() - start_time > self.timeout:
						hit_timeout = True
						break
					# If we're not done, and not timed out yet,
					# just wait
					if retval is None:
						time.sleep(0.25)

				# If we hit a timeout, terminate, and
				# get return code
				if hit_timeout is True:
					proc.terminate()
					retval = proc.wait()

			# Finally get the output, and return back
			o, e = proc.communicate()
			self.output['retval'] = retval
			self.output['output'] = o.strip()

		else:
			# If we couldn't connect to the host,
			# return back
			self.output['retval'] = -1
			self.output['output'] = 'down'

		return

class command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):

	def getRunHosts(self, hosts):
		self.mgmt_networks = {}
		run_hosts = []
		self.attrs = self.call('list.host.attr',hosts)
		f = lambda x: x['attr'] == 'stack.network'
		network_attrs = list(filter(f, self.attrs))

		self.mgmt_networks = {}
		for host in hosts:
			g = lambda x: x['host'] == host
			s = list(filter(g, network_attrs))
			if len(s):
				network = s[0]['value']
				if network not in self.mgmt_networks:
					self.mgmt_networks[network] = []
				self.mgmt_networks[network].append(host)

		a = []
		b = []
		for net in self.mgmt_networks:
			h = self.mgmt_networks[net]
			a.extend(h)
			b.extend(self.getHostnames(h, subnet=net))

		for host in hosts:
			if host in a:
				idx = a.index(host)
				run_hosts.append({'host':host, 'name':b[idx]})
			else:
				run_hosts.append({'host':host, 'name':host})

		return run_hosts

class Command(command):
	"""
	Run a command for each specified host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, the command
	is run on all 'managed' hosts. By default, all backend nodes are
	'managed' nodes. To determine if a host is managed, execute:
	'rocks list host attr hostname | grep managed'. If you see output like:
	'backend-0-0: managed true', then the host is managed.
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
		self.run_hosts = self.getRunHosts(self.hosts)

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
