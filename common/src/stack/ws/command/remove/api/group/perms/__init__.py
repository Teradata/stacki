#
# @copyright@
# @copyright@
#

import os, sys
import stack.commands
import stack.django_env
from stack.exception import *

from django.contrib.auth.models import Group
from stack.restapi.models import GroupAccess

class Command(stack.commands.Command):
	"""
	Removes a permission from a group
	<arg name="group" type="string">
	Group Name
	</arg>
	<param name="perm" type="string">
	Permission
	</param>
	"""
	def run(self, params, args):
		if len(args) != 1:
			raise ArgRequired(self, "Group name")
		groupname = args[0]
		(perm,) = self.fillParams([
			("perm",None),
			])
		if perm == None:
			raise ParamRequired(self, "perm")
		try:
			g = Group.objects.get(name=groupname)
		except Group.DoesNotExist:
			raise CommandError(self,
				"Group '%s' does not exist" % (groupname))

		try:
			ga = GroupAccess.objects.get(group=g, command=perm)
		except GroupAccess.DoesNotExist:
			raise CommandError(self,
				"Group '%s' does not has perm '%s'"
				% (groupname, perm))
		ga.delete()
