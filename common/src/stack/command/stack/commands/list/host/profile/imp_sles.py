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
			for line in generator.generate('native'):
				profile.append(line)
			profile.append('</chapter>')

		elif generator.getProfileType() == 'shell':
			profile.append('<chapter name="bash">')
			for line in generator.generate('shell'):
				profile.append(line)
			profile.append('</chapter>')


