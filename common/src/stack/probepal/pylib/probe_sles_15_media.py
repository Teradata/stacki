import pathlib
import re
from operator import itemgetter

from stack.probepal.common import PalletInfo, Probe

class Sles15MediaProbe(Probe):
	'''
	This prober is intended to look for and parse a 'media.1/media' file which indicates a SUSE non-installer ("Packages") iso

	The contents of this file look like:

	SUSE - SLE-15-SP1-Packages-x86_64-Build228.2-Media2.iso
	SLE-15-SP1-Packages-x86_64-Build228.2-Media2.iso
	1
	'''


	def __init__(self, weight=30, desc='media.1/media files - sles15 extra media'):
		super().__init__(weight=weight, desc=desc)

	def probe(self, pallet_root):
		path = pathlib.Path(f'{pallet_root}/media.1/media')
		if not path.is_file():
			return []

		text = path.read_text()

		pattern = re.compile(r'''
			^SUSE\ -\                # preamble
			(?P<os>\w+)-             # match the OS: SLE
			(?P<rel>\w+)-            # match the release: 15
			((?P<servicepack>\w+)-)? # optionally, match the version: SP1
			(?P<disctype>\w+)-       # match the disctype: Packages
			(?P<arch>\w+)-           # match the arch
			.+-                      # the build number of the iso
			\w+(?P<dvd_num>\d+)      # match just the disk number
			''',
			re.VERBOSE
		)

		match = pattern.match(text)
		if not match:
			return []

		getter = itemgetter('os', 'rel', 'servicepack', 'disctype', 'arch', 'dvd_num')

		os, rel, servicepack, disctype, arch, dvd_num = getter(match.groupdict())

		distro_family = None
		if os == 'SLE':
			distro_family = 'sles'

		if servicepack:
			servicepack = servicepack.lower()
		else:
			servicepack = ''

		version = f'{rel}{servicepack}'
		release = f'{distro_family}{rel}'

		name = f'{disctype}-{dvd_num}'

		p = PalletInfo(name, version, release, arch, distro_family, pallet_root, self.__class__.__name__)
		return [p] if p.is_complete() else []
