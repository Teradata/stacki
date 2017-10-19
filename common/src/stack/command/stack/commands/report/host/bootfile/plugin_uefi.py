# @copyright@
# @copyright@

import os
import stack.commands


class Plugin(stack.commands.Plugin):
	"""
	Generate a UEFI specific configuration file
	"""
	def requires(self):
		return []

	def provides(self):
		return 'uefi'

	def run(self, ha):
		for host in ha:
			# If actions aren't specified on the command line
			# get info from the database
			osname = ha[host]['os']
			for interface in ha[host]['interfaces']:
				ip = interface['ip']
				filename = os.path.join(os.path.sep,
					'tftpboot', 'pxelinux', 'uefi', 'grub.cfg-%s' % ip)
				self.owner.addOutput(host, '<stack:file stack:name="%s" \
					stack:owner="root:apache" stack:perms="0664" \
					stack:rcs="off"><![CDATA[' % filename)
				self.owner.runImplementation("%s_uefi" % osname, ha[host])
				self.owner.addOutput(host, ']]></stack:file>')
