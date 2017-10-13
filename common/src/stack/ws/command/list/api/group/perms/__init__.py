#
# @copyright@
# @copyright@
#

import os
import sys
import stack.django_env
import stack.commands
from stack.exception import *

from django.contrib.auth.models import Group
from stack.restapi.models import GroupAccess

class Command(stack.commands.Command):
	"""
	List group permissions
	<arg type="string" name="group">
	List API permissions for one or more groups
	</arg>
	"""
	def run(self, params, args):
		self.groups = []
		if len(args) == 0:
			self.groups = Group.objects.all()
		
		for arg in args: 
			try:
				g = Group.objects.get(name=arg)
			except:
				continue
			self.groups.append(g)
		self.beginOutput()
		for g in self.groups:
			ga = GroupAccess.objects.filter(group=g)
			for group in ga:
				self.addOutput(group.group.name, group.command)
		self.endOutput(header=['Group', 'Command'], trimOwner=False)
				
