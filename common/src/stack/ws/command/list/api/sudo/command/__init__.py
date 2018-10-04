import stack.commands

import stack.django_env
from stack.exception import *

from stack.restapi.models import SudoList

import re

class Command(stack.commands.Command):
	"""
	List all commands on the webservice
	sudo list. This shows the list of
	commands that will be run using sudo
	<example cmd="list api sudo command">
	List commands that will be run using sudo
	</example>
	"""
	def run(self, params, args):
		self.beginOutput()
		for s in SudoList.objects.all():
			self.addOutput(None,[s.command])
		self.endOutput(header=['owner', 'command'], trimOwner = True)
