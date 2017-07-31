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

