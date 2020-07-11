# @copyright@
# @copyright@

import stack.commands


class PXEImplementation(stack.commands.Implementation):

	def get_tftpboot_filename(self, mac_address):
		# way more human friendly then the old hex ip address stuff
		return '-'.join(map(lambda x: x.lower(), mac_address.split(':')))
	    
	def get_sux_header(self, filename):
		return f'<stack:file stack:name="{filename}" stack:owner="root:apache" stack:perms="0664" stack:rcs="off"><![CDATA["""'

	def get_sux_trailer(self):
		return f'</stack:file>'
