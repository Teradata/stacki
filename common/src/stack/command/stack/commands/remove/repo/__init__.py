from stack.argument_processors.repo import RepoArgProcessor
import stack.commands
import stack.deferable
from stack.exception import CommandError


class Command(RepoArgProcessor, stack.commands.remove.command):
	"""
	Remove remote software repositories from stacki.

	<arg type='string' name='repo'>
	A list of repo's to remove.  This can be the repo name or alias.
	</arg>

	<example cmd='remove repo ceph_pkgs'>
	Remove the 'ceph_pkgs' repository from stacki
	</example>
	"""

	@stack.deferable.rewrite_frontend_repo_file
	def run(self, params, args):
		if not args:
			raise CommandError(self, 'either a repo name or alias must be specified.')

		for repo in self.get_repos(args):
			self.delete_repo(repo.alias)

