# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
import stack.gen
import stack.redhat.gen


class Implementation(stack.commands.list.host.profile.implementation):

	def generator(self):
		return stack.redhat.gen.Generator()

	def XXchapter(self, generator, profile):

		if generator.getProfileType() == 'native':
			profile.append('<chapter name="kickstart">')
			for section in [ 'native',
					 'packages',
					 'pre',
					 'post',
					 'boot' ]:
				profile.append('\t<section name="%s">' % section)
				for line in generator.generate(section):
					profile.append(line)
				profile.append('\t</section>')
			profile.append('</chapter>')

		elif generator.getProfileType() == 'bash':
			profile.append('<chapter name="main">')
			for line in generator.generate('bash'):
				profile.append(line)
			profile.append('</chapter>')


