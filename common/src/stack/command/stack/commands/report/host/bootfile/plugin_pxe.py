# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import os
import stack.commands


class Plugin(stack.commands.Plugin):

	def run(self, ha):

		for host in ha.keys():

			h	 = ha[host]
			filename = h['filename']
			osname   = h['os']

			if not filename:
				continue

			filename = os.path.join(os.path.sep, 
						'tftpboot', 'pxelinux', 
						'pxelinux.cfg', filename)

			self.owner.addOutput(host, '<stack:file stack:name="%s" stack:owner="root:apache" stack:perms="0664" stack:rcs="off"><![CDATA[' % filename)
			self.owner.runImplementation("%s_pxe" % osname, h)
			self.owner.addOutput(host, ']]></stack:file>')

