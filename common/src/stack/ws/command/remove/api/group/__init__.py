#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.exception import *
import stack.django_env

from django.contrib.auth.models import Group

class Command(stack.commands.Command):
	"""
	Remove a group from the API
	<arg type="string" name="group">
	Group to remove
	</arg>
	"""
	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, "Group Name")
		for arg in args:
			if arg == "default":
				raise CommandError(self, "Cannot remove 'default' group")
			try:
				g = Group.objects.get(name=arg)
				g.delete()
			except:
				pass
