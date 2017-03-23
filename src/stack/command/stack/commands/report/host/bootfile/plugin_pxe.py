# @SI_Copyright@
# @SI_Copyright@

import os
import sys
import stack.commands

class Plugin(stack.commands.Plugin):
	def run(self, args):
		hosts = args[0]
		action = args[1]
		for host in hosts:
			# If actions aren't specified on the command line
			# get info from the database
			if not action:
				o = self.owner.call('list.host.boot',[host])
				action = o[0]['action']
			# Run the OS-specific implementation
			osname = self.owner.db.getHostOS(host)
			hex_ip_list = self.owner.getHostHexIP(host)
			if hex_ip_list == []:
				return

			for ip in hex_ip_list:
				filename = '/tftpboot/pxelinux/pxelinux.cfg/%s' % ip
				self.owner.addOutput(host, '<stack:file stack:name="%s" stack:owner="root:apache" stack:perms="0664" stack:rcs="off"><![CDATA[' % filename)
				self.owner.runImplementation("%s_pxe" % osname, [host, action])
				self.owner.addOutput(host, ']]></stack:file>')
