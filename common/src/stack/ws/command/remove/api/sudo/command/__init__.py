import stack.commands

import stack.django_env
from stack.exception import *

from stack.restapi.models import SudoList

import re

class Command(stack.commands.Command):
	"""
	Remove a command from the webservice
	sudo list.
	<param type="string" name="command">
	Command to remove from sudo list
	</param>
	<example cmd="remove api sudo command command='sync host config'">
	Remove "sync host config" command from the sudo list.
	</example>
	"""
	def run(self, params, args):
		(command, sync ) = self.fillParams([
			("command", None),
			("sync", True)
			])
		if not command:
			raise ParamRequired(self, "Command")
		sync = self.str2bool(sync)
		try:
			s = SudoList.objects.get(command=command)
			s.delete()
			if sync:
				self.command("sync.api.sudo.command")
		except SudoList.DoesNotExist:
			raise CommandError(self, f"Command {command} is not a sudo command")
