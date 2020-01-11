from stack.argument_processors.box import BoxArgProcessor
from stack.argument_processors.host import HostArgProcessor
from stack.argument_processors.repo import RepoArgProcessor

import stack.commands
from stack.repo import build_repo_files, yum_repo_template

class Command(BoxArgProcessor,
	HostArgProcessor,
	RepoArgProcessor,
	stack.commands.report.command):
	"""
	Create a report that describes the repository configuration file
	that should be put on hosts.

	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>

	<example cmd='report host repo backend-0-0'>
	Create a report of the repository configuration file for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()

		hosts = self.getHostnames(args)
		self.host_attrs = self.getHostAttrDict(hosts)

		# get the boxes that are actually in use by the hosts we're running against
		box_repos = {
			attrs['box']: self.get_repos_by_box(attrs['box'])
			for attrs in self.host_attrs.values()
		}

		# only generate repo file contents once for each box.
		self.box_repo_data = {}
		for box, repo_data in box_repos.items():
			# replace the variables in the yum repo with data from the repo tables
			repo_lines = build_repo_files(repo_data, yum_repo_template)
			self.box_repo_data[box] = '\n\n'.join(repo_lines)

		# now for each host, build its customized repo file
		for host in hosts:
			# TODO: ubuntu
			imp = 'rpm'
			self.runImplementation(imp, (host,))

		self.endOutput(padChar='', trimOwner=True)
