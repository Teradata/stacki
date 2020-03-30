#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import base64
import json
import os
import sys

# note to future linters: stack.django_env must come before the actual django imports
import stack.django_env
from django.contrib.auth.models import User, Group

from stack.password import Password
import stack.commands
from stack.commands import HostArgProcessor
from stack.exception import *


class Command(HostArgProcessor, stack.commands.Command):
	"""
	Create a user to the REST API.
	This command will print out a JSON
	string that contains the Username, API Key,
	and Hostname of the API server.
	<arg name="username" type="string">
	Username of the user being created
	</arg>

	<param name="group" type="string">
	Comma-separated list of groups that the
	user should belong to. Default is "default".
	</param>

	<param name="admin" type="bool">
	Admin type user account. Default is "False"
	</param>

	<example cmd="add user greg admin=True">
	Adds a user called 'greg' with admin privileges
	to the API
	</example>
	"""

	def gen_random_pw(self):
		p = Password()
		return p.get_cleartext_pw()

	def run(self, params, args):
		# Get Username
		if len(args) != 1:
			raise ArgRequired(self, "username")
		username = args[0]
		if not username.isalnum():
			raise ArgError(self, "username", "must be alphanumeric")

		# Get Groups that you want the user to belong to
		(g, admin) = self.fillParams([
				("group", "default"),
				("admin", "False"),
				])
		group_list = g.split(',')

		# Check to see if username is taken
		try:
			u = User.objects.get(username = username)
		except User.DoesNotExist:
			u = None
		if u:
			raise CommandError(self,
				"Username %s is already in use"
				% username)


		admin = self.str2bool(admin)

		passwd = self.gen_random_pw()

		groups = []
		for group in group_list:
			try:
				g = Group.objects.get(name = group)
				groups.append(g)
			except Group.DoesNotExist:
				raise CommandError(self, "Group %s does not exist." % group )


		u = User(username = username)
		u.set_password(passwd)
		u.is_superuser = admin
		u.save()
		u.groups.set(groups)

		hostname = self.getHostnames(['localhost'])[0]
		domainname = self.getHostAttr('localhost','domainname')
		if domainname and domainname != '':
			hostname = "%s.%s" % (hostname, domainname)

		self.beginOutput()
		self.addOutput(username, [hostname, passwd])
		self.endOutput(header=["username", "hostname","key"])
