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

from django.contrib.auth.models import Group
from stack.restapi.models import GroupAccess
from stack.commands.add.api import checkCommand

from stack.exception import *

class Command(stack.commands.Command):
	"""
	Add permissions to a group.
	<arg name="group" type="string">
	Group name to add permissions to
	</arg>
	<param name="perm" type="string">
	Regular expression of permission
	</param>
	<example cmd='add group perms default perm="report.*"'>
	All users in the 'default' group to run 'report' commands
	</example>
	"""
	def run(self, params, args):
		if len(args) != 1:
			raise ArgRequired(self, "group name")
		groupname = args[0]
		(perm,) = self.fillParams([
			("perm","list.*"),
			])

		# Check if group exists
		checkCommand(self, perm)
		try:
			g = Group.objects.get(name=groupname)
		except Group.DoesNotExist:
			raise CommandError(self, 'Group %s does not exist' % groupname)

		try:
			ga = GroupAccess.objects.get(group = g, command=perm)
		except GroupAccess.DoesNotExist:
			ga = GroupAccess.objects.create(group=g, command=perm)
			ga.save()
