#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands

import stack.django_env
from stack.exception import *

from django.contrib.auth.models import User

class Command(stack.commands.Command):
	"""
	Remove API User.
	<arg name="user" type="string">
	User to remove
	</arg>
	"""
	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, "Username")
		if '%' in args:
			raise CommandError(self, "Cannot use '%' as username")
		for arg in args:
			try:
				u = User.objects.get(username=arg)
				u.delete()
			except:
				raise CommandError(self, "Cannot find user %s" % arg)
