# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#

import os
import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'subnets'


	def run(self, args):
		(oldhost, oldip, password) = args

		network = self.owner.getHostAttr('localhost',
			'Kickstart_PublicNetwork')
		netmask = self.owner.getHostAttr('localhost',
			'Kickstart_PublicNetmask')
		domainname = self.owner.getHostAttr('localhost',
			'Kickstart_PublicDNSDomain')

		print('Updating subnets')

		self.owner.command('set.network.subnet', [ 'public', network ])
		self.owner.command('set.network.netmask', [ 'public', netmask ])

		#
		# we need to 'system' out here because if the domain doesn't
		# change, then 'set network zone' will return an error if
		# we try to set the zone to the same value.
		#
		os.system('/opt/stack/bin/stack set network zone public ' +
			'%s > /dev/null 2>&1' % domainname)

