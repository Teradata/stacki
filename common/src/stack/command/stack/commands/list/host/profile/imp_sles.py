#! /opt/stack/bin/python
#
# @SI_Copyright@
# @SI_Copyright@

import string
import stack.commands
import stack.gen
import stack.sles.gen


class Implementation(stack.commands.list.host.profile.implementation):
	
	def generator(self):
		return stack.sles.gen.Generator()

	def chapter(self, generator, profile):
		if generator.getProfileType() == 'native':
			profile.append('<chapter name="yast">')
			for section in [ 'native' ]:
				profile.append('\t<section name="%s">' % section)
				for line in generator.generate(section):
					profile.append(line)
				profile.append('\t</section>')
			profile.append('</chapter>')

		elif generator.getProfileType() == 'shell':
			profile.append('<chapter name="bash">')
			profile.append('#! /bin/bash')
			for section in [ 'packages' ]:
				profile.append('\t<section name="%s">' % section)
				for line in generator.generate(section):
					profile.append(line)
				profile.append('\t</section>')
			profile.append('</chapter>')


