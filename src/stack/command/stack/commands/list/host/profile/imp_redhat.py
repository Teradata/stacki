# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#

import string
import stack.commands
import stack.gen
import stack.redhat.gen


class Implementation(stack.commands.list.host.profile.implementation):

	def generator(self):
		return stack.redhat.gen.Generator()

	def chapter(self, generator, profile):

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

		elif generator.getProfileType() == 'shell':
			profile.append('<chapter name="bash">')
			profile.append('#! /bin/bash')
			for section in [ 'packages',
					 'post',
					 'boot' ]:
				profile.append('\t<section name="%s">' % section)
				for line in generator.generate(section):
					profile.append(line)
				profile.append('\t</section>')
			profile.append('</chapter>')


