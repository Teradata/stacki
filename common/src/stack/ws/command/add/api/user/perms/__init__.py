#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
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
	Set permission for user
	<arg type="string" name="user">
	Username
	</arg>
	<param type="string" name="perm">
	RegExp of Commands that the user is allowed to run.
	</param>
	<example cmd="add user perm user1 perm='list.host.*'">
	Allows 'user1' to run all commands that conform to the
	regular expression "list.host.*".
	</example>
	"""
	def run(self, params, args):
		if len(args) != 1:
			raise ArgRequired(self, "Username")
		username = args[0]
		(perm,) = self.fillParams([
			("perm", None),
			])
		
		if not perm:
			raise ParamRequired(self, "Permission")
		try:
			u = User.objects.get(username=username)
		except User.DoesNotExist:
			raise CommandError('User %s does not exist' % username)

		try:
			ua = UserAccess.objects.get(user = u, command=perm)
		except UserAccess.DoesNotExist:
			ua = UserAccess.objects.create(user=u, command=perm)
			ua.save()
			
