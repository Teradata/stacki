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

class Command(stack.commands.Command):
	"""
	List all the users allowed to access
	the API framework.
	<example cmd='list api group'>
	List all the users allowed to access
	the API framework.
	</example>
	"""
	def run(self, params, args):
		g = Group.objects.all()
		self.beginOutput()
		for group in g:
			userlist = []
			for u in group.user_set.all():
				userlist.append(u.username)
			userstring = " ".join(userlist)
			self.addOutput(group.name, userstring)
		self.endOutput(header=["GROUP","USERS"], trimOwner=False)
