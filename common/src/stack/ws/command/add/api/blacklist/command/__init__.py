import stack.commands

import stack.django_env
from stack.exception import *

from stack.restapi.models import BlackList
from stack.commands.add.api import checkCommand

import re

class Command(stack.commands.Command):
	"""
	Add a command to the webservice
	blacklist. This disallows the
	command from running, by anyone,
	including the admin. This has the
	granularity of a command. This means
	that you can only blacklist individual
	commands, and not entire verbs of
	commands.
	<param type="string" name="command">
	Command to blacklist
	</param>
	<example cmd="add blacklist command command='list host message'">
	Add "list host message" command to the blacklist.
	</example>
	"""
	def run(self, params, args):
		(command, ) = self.fillParams([
			("command", None)
			])
		if not command:
			raise ParamRequired(self, "Command")

		checkCommand(self, command)

		try:
			b = BlackList.objects.get(command=command)
			if b:
				raise CommandError(self, "Command %s is already blacklisted" % command)
		except BlackList.DoesNotExist:
			b = BlackList(command=command)
			b.save()
