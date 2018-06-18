# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, ParamError


class Command(stack.commands.set.host.command):
	"""
	Sends a "power" command to a host. Valid power commands are: on, off and reset. This
	command uses IPMI to change the power setting on a host.
	
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='command' optional='0'>
	The power command to execute. Valid power commands are: "on", "off" and "reset".
	</param>

	<param type='boolean' name='debug' optional='1'>
	Print debug output from the ipmitool command.
	</param>

	<example cmd='set host power stacki-1-1 command=reset'>
	Performs a hard power reset on host stacki-1-1.
	</example>
	"""

	def doPower(self, host, ipmi_ip, cmd):
		import subprocess
		import shlex

		if not ipmi_ip:
			return

		username = self.getHostAttr(host, 'ipmi_username')
		if not username:
			username = 'root'

		password = self.getHostAttr(host, 'ipmi_password')
		if not password:
			password = 'admin'

		ipmi = 'ipmitool -I lanplus -H %s -U %s -P %s chassis power %s' \
			% (ipmi_ip, username, password, cmd)

		p = subprocess.Popen(shlex.split(ipmi), stdout = subprocess.PIPE,
			stderr = subprocess.STDOUT)
		out, err = p.communicate()

		if self.debug:
			self.beginOutput()
			self.addOutput(host, out.decode())
			self.endOutput(padChar='', trimOwner=True)
		

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'host')

		cmd, debug = self.fillParams([ ('command', None, True), ('debug', 'n') ])

		if cmd == 'status':
			#
			# used by "stack list host power" -- this is an easy way in which to
			# share code between the two commands
			#
			# set 'debug' to 'y' in order to get output from the status command
			#
			debug = 'y'
		elif cmd not in [ 'on', 'off', 'reset' ]:
			raise ParamError(self, 'command', 'must be "on", "off" or "reset"')
		
		self.debug = self.str2bool(debug)
		
		for host in self.getHostnames(args):
			for o in self.call('list.host.interface', [ host ]):
				if o['interface'] == 'ipmi':
					self.doPower(host, o['ip'], cmd)
					break

