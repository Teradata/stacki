import pathlib
import shlex

from stack.probepal.common import PalletInfo, Probe

class DebianProbe(Probe):
	'''
	This prober is intended to look for and parse a .disk/info file which indicates an debian ISO

	The contents of this file look like:

	Debian GNU/Linux 10.4.0 "Buster" - Official amd64 DVD Binary-1 20200509-10:26
	'''

	arch_map = {'amd64': 'x86_64'}

	def __init__(self, weight=30, desc='.disk/info files - debian'):
		super().__init__(weight=weight, desc=desc)

	def probe(self, pallet_root):
		path = pathlib.Path(f'{pallet_root}/.disk/info')
		if not path.is_file():
			return []

		content = path.read_text().strip()

		fields = shlex.split(content)

		if len(fields) < 10 or fields[0:2] != 'Debian GNU/Linux'.split():
			return []


		name, version, release, arch, distro_family = (
			fields[0],
			fields[2],
			fields[3].strip('"'), # code name as release
			self.arch_map.get(fields[-4]),
			'debian'
		)

		p = PalletInfo(name, version, release, arch, distro_family, pallet_root, self.__class__.__name__)
		return [p] if p.is_complete() else []

