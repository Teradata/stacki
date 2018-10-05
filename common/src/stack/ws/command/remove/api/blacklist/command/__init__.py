import stack.commands

import stack.django_env
from stack.exception import *

from stack.restapi.models import BlackList

import re

class Command(stack.commands.Command):
	"""
	Remove a command from the webservice
	blacklist.
	<param type="string" name="command">
	Command to remove from blacklist
	</param>
	<example cmd="remove api blacklist command command='list host message'">
	Remove "list host message" command from the blacklist.
	</example>
	"""
	def run(self, params, args):
		(command, ) = self.fillParams([
			("command", None)
			])
		if not command:
			raise ParamRequired(self, "Command")
		try:
			b = BlackList.objects.get(command=command)
			b.delete()
		except BlackList.DoesNotExist:
			raise CommandError(self, "Command %s is not blacklisted" % command)
