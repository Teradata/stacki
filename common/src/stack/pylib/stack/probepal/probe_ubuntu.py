import pathlib
import shlex

from stack.probepal.common import PalletInfo, Probe, UnrecognizedPallet

class UbuntuProbe(Probe):
	'''
	This prober is intended to look for and parse a .disk/info file which indicates an ubuntu ISO

	The contents of this file look like:

	Ubuntu 19.04 "Disco Dingo" - Release amd64 (20190416)
	'''

	arch_map = {'amd64': 'x86_64'}

	def __init__(self, weight=10, desc='.disk/info files - ubuntu'):
		super().__init__(weight, desc)

	def probe(self, pallet_root):
		path = pathlib.Path(f'{pallet_root}/.disk/info')
		if not path.is_file():
			return None

		content = path.read_text().strip()

		fields = shlex.split(content)
		if not fields[0].startswith('Ubuntu') or len(fields) < 6:
			return None

		# "release" is a stacki term. For Ubuntu, that's the first two date portions
		name, version, release, arch, distro_family = (
			fields[0],
			fields[1],
			# for ubuntu, stacki's 'release' is the date portion of the version number
			'ubuntu' + '.'.join(fields[1].split('.')[0:2]),
			# LTS releases have an extra field, but 'arch' is always second to last
			self.arch_map.get(fields[-2]),
			'Ubuntu'
		)

		p = PalletInfo(name, version, release, arch, distro_family)
		if p.is_complete():
			return p
		else:
			raise UnrecognizedPallet()
