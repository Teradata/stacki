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



