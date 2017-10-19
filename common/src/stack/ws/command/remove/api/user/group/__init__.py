#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands

import stack.django_env
from stack.exception import *

from django.contrib.auth.models import User, Group

class Command(stack.commands.Command):
	"""
	Remove user from an existing group
	<arg type="string" name="user">
	User
	</arg>
	<param type="string" name="group">
	Group to remove the user from.
	</param>
	"""
	def run(self, params, args):
		if len(args) != 1:
			raise ArgRequired(self, "User")
		(group,) = self.fillParams([
			("group", None)
			])

		if group == None:
			raise ParamRequired(self, "Group")


		try:
			g = Group.objects.get(name=group)
		except Group.DoesNotExist:
			raise CommandError(self, "Group '%s' does not exist" % group)

		userlist = []
		for arg in args:
			try:
				u = User.objects.get(username=arg)
				userlist.append(u)
			except User.DoesNotExist:
				raise CommandError(self, "Cannot find user '%s'" % user)
		for user in userlist:
			user.groups.remove(g)
			user.save()

