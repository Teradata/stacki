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
#
# $Log:$
#

import os
import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'postfix'


	def run(self, args):
		(oldhost, oldip, password) = args

		shortname = self.owner.getHostAttr('localhost',
			'Kickstart_PrivateHostname')
		domainname = self.owner.getHostAttr('localhost',
			'Kickstart_PublicDNSDomain')

		print('Updating postfix')

		file = open('/etc/postfix/sender-canonical', 'w+')
		file.write('@local @%s.%s\n' % (shortname, domainname))
		file.close()

		os.system('/usr/sbin/postmap /etc/postfix/sender-canonical')

		file = open('/etc/postfix/recipient-canonical', 'w+')
		file.write('root@%s root\n' % (domainname))
		file.close()

		os.system('/usr/sbin/postmap /etc/postfix/recipient-canonical')

