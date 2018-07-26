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

from django.contrib.auth.models import Group

class Command(stack.commands.Command):
	"""
	Add a group to the REST API Group list
	<arg name="group" type="string">
	Group Name
	</arg>
	"""
	def run(self, params, args):
		# Allow creation of one group only
		if len(args) != 1:
			raise ArgRequired(self, "group name")
		groupname = args[0]

		# Check to see if group name is alphanumeric
		if not groupname.isalnum():
			raise ArgError(self, 
				"Group name", "must be alphanumeric")

		# Check to see if group exists
		try:
			g = Group.objects.get(name=groupname)
		except Group.DoesNotExist:
			g = None
		if g:
			raise CommandError(self, "Group %s is already in use" % g)

		# Create group
		g = Group()
		g.name = groupname
		g.save()
