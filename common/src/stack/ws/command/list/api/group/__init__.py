#
# @copyright@
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
	<dummy />
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
