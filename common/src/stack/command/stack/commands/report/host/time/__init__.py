#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands


class Command(stack.commands.HostArgumentProcessor, stack.commands.report.command):
	"""
	Create a time configuration report (NTP or chrony).

	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>
	
	<example cmd='report host time backend-0-0'>
	Create a time configuration file for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()

		hosts = self.getHostnames(args)
		for host in hosts:

			attrs = {}
			for row in self.call('list.host.attr', [ host ]):
				attrs[row['attr']] = row['value']

			protocol   = attrs.get('time.protocol')
			appliance  = attrs.get('appliance')
			timeserver = attrs.get('time.server')

			if not timeserver:
				if appliance == 'frontend':
					timeserver = attrs.get('Kickstart_PublicNTPHost')
				else:
					timeserver = attrs.get('Kickstart_PrivateNTPHost')

			self.runImplementation('time_%s' % protocol,
				(host, appliance, timeserver))

		self.endOutput(padChar='', trimOwner=True)


