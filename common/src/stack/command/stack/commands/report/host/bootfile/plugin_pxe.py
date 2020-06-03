# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import stack.commands


class Plugin(stack.commands.Plugin):
	"""
	Generate a PXE specific configuration file
	"""

	def provides(self):
		return 'pxe'

	def run(self, ha):

		for host in ha:
			if 'interfaces' not in ha[host]:
				continue
			if ha[host]['os'] is None or ha[host]['appliance'] == 'raspberry':
				continue
			for interface in ha[host]['interfaces']:
				filename = os.path.join(os.path.sep, 
							'tftpboot', 
							'pxelinux', 
							'pxelinux.cfg', # IP as Hex
							''.join(map(lambda x: '%02X' % int(x), interface['ip'].split('.'))))
				self.owner.addOutput(host, """
<stack:file stack:name="%s" stack:owner="root:apache" stack:perms="0664"
            stack:rcs="off"><![CDATA[""" % filename)
				self.owner.runImplementation("%s_pxe" % ha[host]['os'], 
							     (ha[host], interface))
				self.owner.addOutput(host, ']]>\n</stack:file>')
