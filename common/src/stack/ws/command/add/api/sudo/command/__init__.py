import stack.commands

import stack.django_env
from stack.exception import *

from stack.restapi.models import SudoList

from stack.commands.add.api import checkCommand

import re

class Command(stack.commands.Command):
	"""
	Add a command, or a set of commands, to the webservice
	sudo list. This allows the webservice to sudo up to
	root to run the commands. It can take a regular expression
	or an individual command.
	<param type="string" name="command">
	Command to add to sudo list. Format of this command is
	{ verb } [ object ... ] [ * ]
	</param>
	<example cmd="add sudo command command='sync config'">
	Add "sync config" command to the sudolist.
	</example>
	<example cmd="add sudo command command='load *'">
	Add "sync config" command to the sudolist.
	</example>
	"""
	def run(self, params, args):
		(command, sync) = self.fillParams([
			("command", None),
			("sync", True)
			])
		if not command:
			raise ParamRequired(self, "Command")
		
		sync = self.str2bool(sync)
		checkCommand(self, command)

		try:
			s = SudoList.objects.get(command=command)
			if s:
				raise CommandError(self, f"Command {command} is already in sudo list")
		except SudoList.DoesNotExist:
			s = SudoList(command=command)
			s.save()
			if sync:
				self.command("sync.api.sudo.command")
