import pathlib
import configparser
import re

from stack.probepal.common import PalletInfo, Probe

class ProductMDProbe(Probe):
	'''
	This prober is intended to look for and parse a .treeinfo file in productmd format which indicates a rhel 7+ or sles15 iso.  productmd is a specific flavor of ini file - it has its own python library, which this code is trying to avoid importing.

	The contents of this file look like:

	[base_product]
	name = Red Hat Enterprise Linux
	short = RHEL
	version = 8

	[general]
	; WARNING.0 = This section provides compatibility with pre-productmd treeinfos.
	; WARNING.1 = Read productmd documentation for details about new format.
	arch = x86_64
	family = Supplementary
	name = Supplementary 8.0.0
	packagedir = Packages
	platforms = x86_64
	repository = .
	timestamp = 1552506294
	variant = Supplementary
	variants = Supplementary
	version = 8.0.0

	[header]
	type = productmd.treeinfo
	version = 1.2

	[media]
	discnum = 1
	totaldiscs = 1

	[release]
	is_layered = true
	name = Supplementary
	short = Supp
	version = 8.0.0
	'''


	def __init__(self, weight=10, desc='treeinfo files - rhel-based, sles15'):
		super().__init__(weight=weight, desc=desc)

	def probe(self, pallet_root):
		path = pathlib.Path(f'{pallet_root}/.treeinfo')
		if not path.is_file():
			return []

		name, version, release, arch, distro_family = [None] * 5
		is_install_media = False

		treeinfo = configparser.ConfigParser()
		treeinfo.read(path)
		try:
			if 'release' in treeinfo:
				version = treeinfo['release']['version'].lower()
				full_version = version.replace(' ', '')
				maj_version = re.split('\.| ', version)[0]
				version = full_version

				name = treeinfo['release']['name']
				shortname = treeinfo['release']['short']

				if name == 'Red Hat Enterprise Linux':
					name = 'RHEL'
				elif name == 'SUSE Linux Enterprise':
					name = 'SLES'
					distro_family = 'sles'
				else:
					name = shortname

				if name and not distro_family:
					distro_family = 'redhat'

				if name == 'Fedora':
					release = 'fedora' + maj_version
				else:
					release = distro_family + maj_version

			if 'base_product' in treeinfo:
				# base_product appears in supplementary isos
				base = treeinfo['base_product']['short']
				name = f'{base}-{name}'

			if 'general' in treeinfo:
				arch = treeinfo['general']['arch']

			if name and name in ['SLES', 'RHEL']:
				is_install_media = True
		except KeyError:
			return []

		p = PalletInfo(name, version, release, arch, distro_family, pallet_root, self.__class__.__name__, is_install_media)
		return [p] if p.is_complete() else []
