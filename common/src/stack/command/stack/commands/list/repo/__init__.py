from stack.argument_processors.repo import RepoArgProcessor
import stack.commands

class Command(RepoArgProcessor, stack.commands.list.command):
	"""
	List software repositories available on the system

	<param optional='1' type='boolean' name='expanded'>
	If set to true, also list out additional information that stacki knows about the repo.
	</param>

	<example cmd='list repo'>
	List info for all known repos
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()

		expanded, = self.fillParams([
			('expanded', 'false'),
			])

		expanded = self.str2bool(expanded)

		for repo in self.get_repos(args):
			name, *data = repo
			if expanded:
				# assumes all 0/1 values in 'data' are boolean.  True today.  Thanks mysql!
				data = [self.str2bool(str(i)) if i in [0,1] else i for i in data]
			else:
				data = data[0:2]
				
			self.addOutput(name, data)

		if expanded:
			header = [c for c in self.REPO_COLUMNS if c != 'pallet_id']
			header.append('pallet name')
		else:
			header = self.REQUIRED_REPO_COLUMNS
		self.endOutput(header, trimOwner=False)
