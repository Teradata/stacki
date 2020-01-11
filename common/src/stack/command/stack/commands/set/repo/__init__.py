# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from collections import namedtuple

import stack.commands
from stack.argument_processors.repo import RepoArgProcessor
from stack.exception import CommandError


class Command(RepoArgProcessor, stack.commands.Command):
	"""
	Set values for the fields in a repo.
	Note that a sync is still required to enact this change.

	<arg type='string' name='repo'>
	The name or alias of the repo on which to set these options.
	</arg>

	<param type='string' name='name'>
	Modify the name of the repo.
	</param>

	<param type='string' name='alias'>
	Modify the alias of the repo.
	</param>

	<param type='string' name='url'>
	Modify the url of the repo.
	</param>

	<param type='boolean' name='autorefresh'>
	Modify whether or not the repo will be autorefreshed when package manage commands are used.
	</param>

	<param type='boolean' name='assumeyes'>
	Modify whether to default to implicitly agreeing to pacakges for the repo.
	</param>

	<param type='string' name='type'>
	Modify what type of repo this is (currently supported are 'rpm-md', 'yast').
	rpm-md repo's must contain a repodata directory. yast repo's use different metadata
	(such as that found on the install media).
	</param>

	<param type='boolean' name='is_mirrorlist'>
	Modify whether or not 'url' points to a mirror list.
	</param>

	<param type='boolean' name='gpgcheck'>
	Modify whether or not to check gpg signatures for this repo.
	</param>

	<param type='string' name='gpgkey'>
	If using gpg signatures, where to find the gpg key for validation.
	</param>

	<param type='string' name='os'>
	Set which OS this repo serves packages for.
	</param>

	<example cmd='set repo EPEL assumeyes=false autorefresh=yes'>
	Set the EPEL repo to autorefresh, but disable implicit confirmation
	</example>
	"""

	def run(self, params, args):

		if len(args) != 1:
			raise CommandError(self, 'only one repo may be specified at a time')

		repo_name = args[0]

		*params, updating_repo = self.fillParams([
			('name', None),
			('alias', None),
			('url', None),
			('autorefresh', None),
			('assumeyes', None),
			('type', None),
			('is_mirrorlist', None),
			('gpgcheck', None),
			('gpgkey', None),
			('os', self.os),
			('pallet', None), # hidden param -- must be the id of the pallet
			('updating_repo', True),
		])
		updating_repo = self.str2bool(updating_repo)

		RepoStuff = namedtuple('RepoStuff', self.REPO_COLUMNS)
		repo_fields = RepoStuff(*params)

		kw_values = repo_fields._asdict()

		for k, v in dict(kw_values).items():
			if not kw_values[k]:
				del kw_values[k]
			elif k in ['autorefresh', 'assumeyes', 'is_mirrorlist', 'gpgcheck']:
				kw_values[k] = 1 if self.str2bool(v) else 0

		if updating_repo:
			self.update_repo_field(repo_name, **kw_values)
			return

		# not updating_repo (user actually called 'add repo')
		if 'name' in kw_values:
			raise CommandError(self, 'name is an ambiguous parameter when adding a repo')
		kw_values['name'] = repo_name

		if 'url' not in kw_values:
			raise CommandError(self, 'url is a required parameter when adding a repo')

		if 'alias' not in kw_values:
			kw_values['alias'] = repo_name.replace(' ', '-')

		self.insert_repo(**kw_values)
