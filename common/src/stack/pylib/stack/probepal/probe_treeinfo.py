import pathlib

from stack.probepal.common import PalletInfo, Probe, UnrecognizedPallet

class TreeinfoProbe(Probe):
	'''
	This prober is intended to look for and parse a .treeinfo file which indicates a rhel 7+ or sles15 iso

	The contents of this file look like:

	[general]
	name = CentOS-7
	family = CentOS
	timestamp = 1504618609.47
	variant =
	version = 7
	packagedir =
	arch = x86_64

	[stage2]
	mainimage = LiveOS/squashfs.img

	[images-x86_64]
	kernel = images/pxeboot/vmlinuz
	initrd = images/pxeboot/initrd.img
	boot.iso = images/boot.iso

	[images-xen]
	kernel = images/pxeboot/vmlinuz
	initrd = images/pxeboot/initrd.img
	'''


	def __init__(self, weight=10, desc='treeinfo files - rhel-based, sles15'):
		super().__init__(weight, desc)

	def probe(self, pallet_root):
		path = pathlib.Path(f'{pallet_root}/.treeinfo')
		if not path.is_file():
			return None

		lines = path.read_text().splitlines()

		name, version, release, arch, distro_family = [None] * 5

		for line in lines:
			kv = line.split('=')
			if len(kv) != 2:
				continue

			key, value = kv[0].strip(), kv[1].strip()

			if key == 'family':
				if value == 'Red Hat Enterprise Linux':
					name = 'RHEL'
				elif value.startswith('CentOS'):
					name = 'CentOS'
				elif value.startswith('Fedora'):
					name = 'Fedora'
				elif value.startswith('Oracle'):
					name = 'OLE'
				elif value.startswith('Scientific'):
					name = 'SL'
				elif value.startswith('SUSE Linux Enterprise'):
					name = 'SLES'
				if name and name == 'SLES':
					distro_family = 'sles'
				elif name and distro_family is None:
					distro_family = 'redhat'

			elif key == 'version':
				version = value
				version = value.split('.')[0]
			elif key == 'arch':
				arch = value

		if name == 'Fedora':
			release = name.lower() + version
		else:
			release = distro_family + version

		discinfo_path = pathlib.Path(f'{pallet_root}/.discinfo')
		if discinfo_path.is_file():
			# .discinfo is rhel-family specific, but has minor version numbering
			lines = discinfo_path.read_text().splitlines()
			try:
				version_str = lines[1].strip().split()
				v = [i for i in version_str if i.replace('.', '1').isdigit()]
				if len(v) == 1:
					version = v[0]
			except IndexError:
				pass

		p = PalletInfo(name, version, release, arch, distro_family)
		if p.is_complete():
			return p
		else:
			raise UnrecognizedPallet()
