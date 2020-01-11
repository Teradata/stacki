from stack.argument_processors.pallet import PalletArgProcessor
from stack.argument_processors.repo import RepoArgProcessor
import stack.commands
from stack.exception import CommandError

class Command(PalletArgProcessor,
	RepoArgProcessor,
	stack.commands.add.command):
	"""
	Add a remote software repository to stacki.

	<arg type='string' name='repo'>
	The name of the repo.
	</arg>

	<param type='string' name='alias' optional='1'>
	An alias for the repository.  This must be a string with no spaces.
	If not provided, the 'name' of the repo will be used, replacing
	spaces with hypens.
	</param>

	<param type='string' name='url' optional='1'>
	The URL of the repository.  This can be a remote URL or a URL pointing
	to the stacki frontend's webserver.  Attributes can be used inside this
	string as jinja variables.  For example,
	'http://{{ Kickstart_PrivateAddress }}/some/path/'
	</param>

	<param type='boolean' name='autorefresh'>
	Whether or not the repo will be autorefreshed when package manage commands are used.
	</param>

	<param type='boolean' name='assumeyes'>
	Whether to default to implicitly agreeing to pacakges for the repo.
	</param>

	<param type='string' name='type'>
	Type of repo this is (currently supported are 'rpm-md', 'yast').  rpm-md repo's must
	contain a repodata directory. yast repo's use different metadata (such as that found
	on the install media).
	</param>

	<param type='boolean' name='is_mirrorlist'>
	Whether or not 'url' points to a mirror list.
	</param>

	<param type='boolean' name='gpgcheck'>
	Whether or not to check gpg signatures for this repo.
	</param>

	<param type='string' name='gpgkey'>
	If using gpg signatures, where to find the gpg key for validation.
	</param>

	<param type='string' name='os'>
	Which OS this repo serves packages for.
	</param>

	<example cmd='add repo coolstuff url=http://{{ Kickstart_PrivateAddress }}/install/random_path/sles12/sles/x86_64'>
	Add a 'coolstuff' repository to stacki.  '{{ Kickstart_PrivateAddress }}'
	will be replaced with that attribute
	</example>

	<example cmd='add repo ceph_pkgs url=http://192.168.0.2/install/pallets/ceph/5.4.2/sles12/sles/x86_64'>
	Add a 'ceph_pkgs' repository to stacki
	</example>

	<example cmd='add repo EPEL url=http://dl.fedoraproject.org/pub/epel assumeyes=false autorefresh=yes'>
	Add the EPEL repository to stacki, enabling autorefresh, but disabling implicit confirmation
	</example>
	"""

	def run(self, params, args):
		if len(args) != 1:
			raise CommandError(self, 'only one repo may be specified at a time')

		self.command('set.repo', self._argv + ['updating_repo=false'])
		return self.rc
