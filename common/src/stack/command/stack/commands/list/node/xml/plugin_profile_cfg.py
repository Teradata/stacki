# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):
	"Creates /opt/stack/etc/profile.cfg"

	def provides(self):
		return 'profile_cfg'

	def run(self, attrs):

		self.owner.addText('<stack:script stack:stage="install-post">\n')
		self.owner.addText('mkdir -p /opt/stack/etc\n')
		self.owner.addText('<stack:file stack:name="/opt/stack/etc/profile.cfg" stack:perms="0640">\n')
		self.owner.addText('[attr]\n')
		for k in sorted(attrs.keys()):
			self.owner.addText('%s = %s\n' % (k, attrs[k]))
		self.owner.addText('</stack:file>\n')
		self.owner.addText('</stack:script>\n')

