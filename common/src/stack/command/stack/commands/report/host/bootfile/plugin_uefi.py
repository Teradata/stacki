# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import stack.commands


class Plugin(stack.commands.Plugin):
	"""
	Generate a UEFI specific configuration file
	"""

	def provides(self):
		return 'uefi'

	def run(self, ha):

		for host in ha:
			for interface in ha[host]['interfaces']:
				filename = os.path.join(os.path.sep,
							'tftpboot', 
							'pxelinux', 
							'uefi', 
							'grub.cfg-%s' % interface['ip'])
				self.owner.addOutput(host, """
<stack:file stack:name="%s" stack:owner="root:apache" stack:perms="0664" 
            stack:rcs="off"><![CDATA[""" % filename)
				self.owner.runImplementation("%s_uefi" % ha[host]['os'], 
							     (ha[host], interface))
				self.owner.addOutput(host, ']]>\n</stack:file>')
