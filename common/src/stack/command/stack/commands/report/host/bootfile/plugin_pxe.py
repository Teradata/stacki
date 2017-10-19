# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import stack.commands


class Plugin(stack.commands.Plugin):

	def run(self, ha):

		for host in ha.keys():

			h	 = ha[host]
			osname   = h['os']

			for interface in h['interfaces']:
				#
				# Compute the HEX IP filename for the host
				#
				ip = interface['ip']
				hexstr = ''
				for i in ip.split('.'):
					hexstr += '%02x' % (int(i))
				hexstr = hexstr.upper()
				filename = os.path.join(os.path.sep, 
						'tftpboot', 'pxelinux', 
						'pxelinux.cfg', hexstr)

				self.owner.addOutput(host, '<stack:file stack:name="%s" \
					stack:owner="root:apache" stack:perms="0664" \
					stack:rcs="off"><![CDATA[' % filename)
				self.owner.runImplementation("%s_pxe" % osname, h)
				self.owner.addOutput(host, ']]></stack:file>')
