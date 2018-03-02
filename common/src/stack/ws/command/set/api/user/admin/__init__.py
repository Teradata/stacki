#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import sys
import stack.django_env

import stack.commands

from stack.exception import *

from django.contrib.auth.models import User, Group

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	Set or unset admin privileges of a user.
	<arg name="Username" type="string">
	Username of user for which to set / unset
	the admin privileges.
	</arg>
	<param name="admin" type="string">
	Set or unset admin privileges.
	</param>
	"""
	def run(self, params, args):
		# Get Username
		if len(args) != 1:
			raise ArgRequired(self, "username")
		username = args[0]
		(admin, ) = self.fillParams([
				("admin", "True"),
				])
		try:
			u = User.objects.get(username = username)
		except User.DoesNotExist:
			raise CommandError(self, "User %s does not exist" % username)

		admin = self.str2bool(admin)
		u.is_superuser = admin
		u.save()
