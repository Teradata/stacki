# @SI_Copyright@
# @SI_Copyright@

import os
import stack.commands

class Plugin(stack.commands.Plugin):
	"Creates /opt/stack/etc/profile.cfg"

	def provides(self):
		return 'profile_cfg'

	def run(self, attrs):

        	self.owner.addText('<stack:post>\n')
                self.owner.addText('mkdir -p /opt/stack/etc\n')
                self.owner.addText('<stack:file stack:name="/opt/stack/etc/profile.cfg" perms="0640">\n')
                self.owner.addText('[attr]\n')
		keys = attrs.keys()
		keys.sort()
                for k in keys:
                        self.owner.addText('%s = %s\n' % (k, attrs[k]))
                self.owner.addText('</stack:file>\n')
                self.owner.addText('</stack:post>\n')

