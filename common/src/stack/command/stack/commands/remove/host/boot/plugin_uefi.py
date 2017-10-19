# @copyright@
# @copyright@

import os
import sys
import stack.commands

class Plugin(stack.commands.Plugin):
	def requires(self):
		return []

	def provides(self):
		return 'uefi'

	def run(self, hosts):
		for host in hosts:
			hex_ip_list = self.owner.getHostHexIP(host)
			if hex_ip_list == []:
				return
			for ip in hex_ip_list:
				filename = '/tftpboot/pxelinux/uefi/grub.cfg-%s' % ip
				if os.path.exists(filename):
					os.unlink(filename)
