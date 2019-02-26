# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import stack.commands


class Plugin(stack.commands.Plugin):
	def requires(self):
		return []

	def provides(self):
		return "pxe"

	def run(self, hosts):
		for host in hosts:
			hex_ip_list = self.owner.getHostHexIP(host)
			if hex_ip_list == []:
				return
			for ip in hex_ip_list:
				filename = '/tftpboot/pxelinux/pxelinux.cfg/%s' % ip
				if os.path.exists(filename):
					os.unlink(filename)
