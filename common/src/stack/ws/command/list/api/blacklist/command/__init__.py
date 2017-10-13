import stack.commands

import stack.django_env
from stack.exception import *

from stack.restapi.models import BlackList

import re

class Command(stack.commands.Command):
	"""
	List all commands on the webservice
	blacklist. This shows the list of
	commands not allowed to run, by anyone,
	including the admin.
	<example cmd="list blacklist command">
	List blacklisted commands
	</example>
	"""
	def run(self, params, args):
		self.beginOutput()
		for b in BlackList.objects.all():
			self.addOutput(None,[b.command])
		self.endOutput(header=['Owner','Command'], trimOwner = True)
