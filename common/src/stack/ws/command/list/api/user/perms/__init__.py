#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import sys
import stack.django_env
import stack.commands

from stack.exception import *

from django.contrib.auth.models import User
from stack.restapi.models import UserAccess,GroupAccess

class Command(stack.commands.Command):
	"""
	List all user permissions. The permissions
	are classified as either permissions that
	belong to the User, or those that are inherited
	from the Group the user belongs to.
	<arg name="user" type="string">
	One or more users
	</arg>
	"""

	def run(self, params, args):
		self.users = []
		if len(args) == 0:
			self.users = User.objects.all()
		for arg in args: 
			try:
				u = User.objects.get(username=arg)
			except:
				continue
			self.users.append(u)
		self.beginOutput()
		for u in self.users:
			perms = {}
			for group in u.groups.all():
				ga = GroupAccess.objects.values('command').filter(group=group)
				for c in ga:
					perms[c['command']] = "G"

			ua = UserAccess.objects.values('command').filter(user=u)
			for c in ua:
				perms[c['command']] = "U"
				
			for command in perms:
				self.addOutput(u.username, [command, perms[command]] )
		self.endOutput(header=['user', 'command', 'source'], trimOwner=False)
				
