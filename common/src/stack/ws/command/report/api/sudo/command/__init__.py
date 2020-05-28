import stack.commands

import stack.django_env
from stack.exception import *

from stack.restapi.models import SudoList
import re

class Command(stack.commands.Command):
	"""
	Report /etc/sudoers.d/stacki_ws file with
	a list of all the commands that can be called
	by apache using sudo
	<example cmd="report api sudo command">
	Output the /etc/sudoers.d/stacki_ws file
	</example>
	"""
	def run(self, params, args):
		commands = [ x['command'] for x in SudoList.objects.values('command') ]
		sudo_list = []
		for command in commands:
			cmd = re.split('[\. \t]+', command)
			if not cmd[-1].endswith("*"):
				cmd.append("*")
			sudo_list.append("/opt/stack/bin/stack %s" % ' '.join(cmd))

		if len(sudo_list) > 0:
			self.beginOutput()
			self.addOutput(None, "<stack:file stack:name='/etc/sudoers.d/stacki_ws' stack:perms='0400' stack:rcs='no'>")
			self.addOutput(None, "# Stacki - SUDO Access to run commands as Apache")
			self.addOutput(None, "Cmnd_Alias STACK_CMDS = %s" % ', \\\n\t'.join(sudo_list))
			self.addOutput(None, "Defaults!STACK_CMDS !requiretty")
			self.addOutput(None, "apache ALL = (root) NOPASSWD:STACK_CMDS")
			self.addOutput(None, "</stack:file>")
			self.endOutput(trimOwner=True)
