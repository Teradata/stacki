#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User, Group
from stack.restapi.models import UserAccess,GroupAccess
import re

class CommandBackend(ModelBackend):
	"""
	This is the Authentication Backend for
	Stacki webservice command permissions.

	The functions here are required by Django
	to check if a certain group, or users have
	certain permissions.
	"""

	# Return Group Permissions
	def get_group_permissions(self, user_obj, obj=None):
		perms = []
		f = lambda x: x['command']
		for group in user_obj.groups.all():
			ga = GroupAccess.objects.values("command").filter(group=group)
			access = map(f, ga)
			perms.extend(access)
		return set(perms)

	# Return all permissions
	def get_all_permissions(self, user_obj, obj=None):
		ua = UserAccess.objects.values("command").filter(user=user_obj)
		f = lambda x: x['command']
		access = map(f, ua)
		perms = self.get_group_permissions(user_obj, obj)
		perms.update(access)
		return perms

	# Check if a user has a certain permission
	def has_perm(self, user_obj, perm, obj=None):
		if not user_obj.is_active:
			return False
		if user_obj.is_superuser:
			return True

		help_re = re.compile("[a-z.]*help")
		if help_re.match(perm):
			return True

		perms = self.get_all_permissions(user_obj, obj)
		# When checking permissions, check to make sure
		# both module name and command line are matched
		# For eg., "list.host" and "list host" should
		# be treated the same way
		# Also, make sure that the matches are exact
		# and not just subset matches
		for p in perms:
			p = re.sub('[ \t]+','.',p)
			r = re.compile(str(p))
			m = r.match(perm)
			if m:
				if m.group() == perm:
					return True

		return False
