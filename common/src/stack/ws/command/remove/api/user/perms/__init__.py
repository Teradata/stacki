#
# @copyright@
# @copyright@
#

import os, sys
import stack.commands
import stack.django_env
from stack.exception import *

from django.contrib.auth.models import User
from stack.restapi.models import UserAccess

class Command(stack.commands.Command):
	"""
	Removes a permission from a user
	<arg name="user" type="string">
	User Name
	</arg>
	<param name="perm" type="string">
	Permission
	</param>
	"""
	def run(self, params, args):
		if len(args) != 1:
			raise ArgRequired(self, "User name")
		username = args[0]
		(perm,) = self.fillParams([
			("perm",None),
			])
		if perm == None:
			raise ParamRequired(self, "perm")
		try:
			u = User.objects.get(username=username)
		except User.DoesNotExist:
			raise CommandError(self,
				"User '%s' does not exist" % (username))

		try:
			ua = UserAccess.objects.get(user=u, command=perm)
		except UserAccess.DoesNotExist:
			raise CommandError(self,
				"User '%s' does not has perm '%s'"
				% (username, perm))
		ua.delete()
