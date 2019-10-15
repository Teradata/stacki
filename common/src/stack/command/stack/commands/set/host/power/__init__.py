# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.mq
import socket
import json
from stack.exception import ArgRequired, ParamError, CommandError
from collections import namedtuple

class Command(stack.commands.set.host.command):
	"""
	Sends a "power" command to a host. Valid power commands are: on, off, reset, and status. This
	command uses IPMI for hardware based hosts to change the power setting.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='command' optional='0'>
	The power command to execute. Valid power commands are: "on", "off", "reset", and "status".
	</param>

	<param type='boolean' name='debug' optional='1'>
	Print debug output from the command. For ipmi capable hosts, prints
	the output from ipmitool.
	</param>

	<param type='string' name='method' optional='1'>
	Set a desired method for communicating to hosts, possible methods
	include but are not limited to ipmi and ssh.
	</param>

	<example cmd='set host power stacki-1-1 command=reset'>
	Performs a hard power reset on host stacki-1-1.
	</example>

	<example cmd='set host power stacki-1-1 command=off method=ssh'>
	Turns off host stacki-1-1 using ssh.
	</example>
	"""
	def mq_publish(self, host, cmd):
		"""
		Publish the power status to the
		message queue
		"""

		ttl = 60*10
		if cmd == 'off':
			ttl = -1

		msg = { 'source' : host,
			'channel': 'health',
			'ttl'    : ttl,
			'payload': '{"state": "power %s"}' % cmd }

		tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		tx.sendto(json.dumps(msg).encode(),
			  ('127.0.0.1', stack.mq.ports.publish))
		tx.close()

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'host')

		cmd, debug, force_imp = self.fillParams([
			('command', None, True),
			('debug', False),
			('method', None)
		])
		host_errors = []
		self.debug = self.str2bool(debug)
		impl_output = namedtuple('output', 'out debug success')

		self.loadImplementation()

		# The first implementation is ipmi by default
		# but can be forced by the method parameter
		# If this is set, only that implementation will be run
		if force_imp:
			if force_imp not in self.impl_list:
				raise ParamError(self, 'method', f'{force_imp} not found as a valid implementation')
			imp_names = [force_imp]

		# Otherwise use all the implementations
		else:

			# Gather all set power implmentations besides ipmi and ssh
			imp_names  = [imp for imp in self.impl_list if imp not in ['ssh', 'ipmi']]

			# Add ipmi to be the first implementation used
			if 'ipmi' in self.impl_list:
				imp_names.insert(0, 'ipmi')

			# Add ssh to be the last implementation used
			if 'ssh' in self.impl_list:
				imp_names.append('ssh')

		if cmd not in ['on', 'off', 'reset', 'status']:
			raise ParamError(self, 'command', 'must be "on", "off", "reset", or "status"')

		for host in self.getHostnames(args):

			# Flag for if an implementation has
			# successfully run. Set to true if an
			# implementation returns success in its output
			imp_success = False
			self.beginOutput()

			# Iterate through each implementation
			# if one succeeds, we are done with the command
			for imp in imp_names:
				imp_msg = self.runImplementation(imp, [host, cmd, impl_output])
				if imp_msg.out:
					self.addOutput(host, imp_msg.out)
				if self.debug:

					# Output debug information if the parameter was set
					if not imp_msg.success and imp_msg.debug:
						self.addOutput(host, f'Failed to set power via {imp}: "{imp_msg.debug}"')

					# Handle if an implementation fails but has no debug information
					elif not imp_msg.success:
						self.addOutput(host, f'Failed to set power via {imp}')
					elif imp_msg.success:
						self.addOutput(host, f'Successfully set power via {imp}')

				# We don't need to run anymore implementations
				# now that one has succeeded for this host
				if imp_msg.success:
					imp_success = True
					self.mq_publish(host, cmd)
					break
			if self.debug and not imp_success:
				self.addOutput(host, f'Could not set power cmd {cmd} on host {host}')
			self.endOutput(padChar='', trimOwner=True)
