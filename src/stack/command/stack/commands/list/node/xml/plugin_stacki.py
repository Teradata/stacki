# @SI_Copyright@
# @SI_Copyright@

import os
from pprint import *
import stack.commands

class Plugin(stack.commands.Plugin):
	"Common <stacki></stacki> section"

	def provides(self):
		return 'stacki'

	def run(self, attrs):

        	self.owner.addText('<stacki>\n')
                self.owner.addText('attributes = %s\n' % pformat(attrs))
                self.owner.addText("""
#
# Generic For All OSes
#
                """)
                self.owner.addText('</stacki>\n')

