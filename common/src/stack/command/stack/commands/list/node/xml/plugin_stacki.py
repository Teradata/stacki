# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from pprint import pformat
import stack.commands


class Plugin(stack.commands.Plugin):
	"Common <stacki></stacki> section"

	def provides(self):
		return 'stacki'

	def run(self, attrs):
		self.owner.addText('<stack:stacki><![CDATA[\n')
		self.owner.addText('attributes = %s\n' % pformat(attrs))
		self.owner.addText(']]></stack:stacki>\n')

