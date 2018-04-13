# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands


class Command(stack.commands.report.host.command):
	"""
	Outputs the Stack Message Queue configuration for a specific host.
	
	<arg optional='0' type='string' name='host' repeat='0'>
	Create MQ configuration for machine named 'host'. If
	no host name is supplied, then generate the configuration file
	for all hosts.
	</arg>
	"""

	def run(self, params, args):

		self.beginOutput()

		for host in self.getHostnames(args):
			self.addOutput(host,
				       '<stack:file stack:name="/etc/sysconfig/stack-mq">')
			self.addOutput(host, 'MASTER=%s' % self.getHostAttr(host, 'Kickstart_PrivateAddress'))
			self.addOutput(host, '</stack:file>')

		self.endOutput(padChar='', trimOwner=True)


