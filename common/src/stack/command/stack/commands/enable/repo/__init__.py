from stack.argument_processors.box import BoxArgProcessor
from stack.argument_processors.repo import RepoArgProcessor
import stack.commands
import stack.deferable
from stack.exception import CommandError

class Command(
	BoxArgProcessor,
	RepoArgProcessor,
	stack.commands.enable.command):
	"""
	Enable a remote software repository for a stacki box

	<arg type='string' name='repo'>
	A list of repos to enable.  This should be the repo's name or alias.
	</arg>

	<param type='string' name='box'>
	The name of the box in which to enable the repo(s). If no
	box is specified the repo is enabled for the default box.
	</param>

	<example cmd='enable repo ceph_pkgs'>
	Enable a 'ceph_pkgs' repository for the default box
	</example>

	<example cmd='enable repo EPEL os-updates-20200123 box=frontend'>
	Enable the EPEL and os-updates-20200123 repositories on the frontend box
	</example>
	"""

	@stack.deferable.rewrite_frontend_repo_file
	def run(self, params, args):
		if not len(args):
			raise CommandError(self, 'One or more repos must be specified')

		box, = self.fillParams([
			('box', 'default'),
		])

		box, = self.get_box_names([box])

		for repo in self.get_repos(args):
			self.enable_repo(repo.alias, box)

		self.call('sync.host.repo', ['localhost'])
