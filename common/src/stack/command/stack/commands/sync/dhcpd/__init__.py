#
# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
#

import stack.commands
import subprocess


class Command(stack.commands.sync.command):
	"""Rebuild the DHCPD configuration files on the frontend and restart the
	DHCPD service"""

	def run(self, params, args):

		self.notify('Sync DHCP\n')

		self.report('report.dhcpd')
		
		subprocess.call(['/sbin/service', 'dhcpd', 'restart'],
				stdout=open('/dev/null'), stderr=open('/dev/null'))
