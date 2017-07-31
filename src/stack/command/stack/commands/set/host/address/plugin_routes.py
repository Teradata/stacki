# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log:$
#

from __future__ import print_function
import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'routes'


	def run(self, args):
		(oldhost, oldip, password) = args

		shortname = self.owner.getHostAttr('localhost',
			'Kickstart_PrivateHostname')
		gateway = self.owner.getHostAttr('localhost',
			'Kickstart_PublicGateway')
		private_gateway = self.owner.getHostAttr('localhost',
			'Kickstart_PrivateGateway')
		ip = self.owner.getHostAttr('localhost',
			'Kickstart_PublicAddress')

		print('Updating routes')

		self.owner.command('remove.host.route',
			[ 'localhost', '0.0.0.0' ])
		self.owner.command('add.host.route',
			[ shortname, '0.0.0.0', gateway, 'netmask=0.0.0.0' ])

		self.owner.command('remove.route', [ oldip ])

		self.owner.command('add.route', [ ip, private_gateway,
			'netmask=255.255.255.255' ]) 

