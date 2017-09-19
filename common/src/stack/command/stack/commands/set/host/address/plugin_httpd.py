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
		return 'httpd'


	def run(self, args):
		(oldhost, oldip, password) = args

		shortname = self.owner.getHostAttr('localhost',
			'Kickstart_PrivateHostname')
		domainname = self.owner.getHostAttr('localhost',
			'Kickstart_PublicDNSDomain')

		print('Updating httpd')

		cmd = '/bin/sed -i '
		cmd += '"s/\(ServerName\).*/\\1 %s.%s/g" ' \
			% (shortname, domainname)
		cmd += '/etc/httpd/conf.d/stack.conf'
		os.system(cmd)

