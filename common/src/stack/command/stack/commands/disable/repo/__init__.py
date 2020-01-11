# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.argument_processors.repo import RepoArgProcessor
from stack.argument_processors.box import BoxArgProcessor
import stack.commands
from stack.exception import CommandError


class Command(BoxArgProcessor, RepoArgProcessor, stack.commands.disable.command):
	"""
	Disables a Repo. The Repo must already be copied on the
	system using the command "stack add repo".

	<arg type='string' name='repo' repeat='1'>
	List of repos to disable. This can be the repo alias or name.
	</arg>

	<param type='string' name='box'>
	The name of the box in which to disable the repo. If no box is
	specified the repo is disabled for the default box.
	</param>

	<example cmd='disable repo local'>
	Disable the repo named "local".
	</example>

	<related>add repo</related>
	<related>enable repo</related>
	<related>list repo</related>
	"""

	def run(self, params, args):
		if not len(args):
			raise CommandError(self, 'One or more repos must be specified')

		box, = self.fillParams([
			('box', 'default'),
		])

		box, = self.get_box_names([box])

		for repo in self.get_repos(args):
			self.disable_repo(repo.alias, box)

		# TODO, only run if frontend box has changed
		# Regenerate stacki.repo
		self._exec("""
			/opt/stack/bin/stack report host repo localhost |
			/opt/stack/bin/stack report script |
			/bin/sh
			""", shell=True)
