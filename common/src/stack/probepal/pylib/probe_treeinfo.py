import pathlib

from stack.probepal.common import PalletInfo, Probe

class TreeinfoProbe(Probe):
	'''
	This prober is intended to look for and parse a .treeinfo file which indicates a centos 7+ iso

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


	def __init__(self, weight=20, desc='treeinfo files - centos7-based'):
		super().__init__(weight=weight, desc=desc)

	def probe(self, pallet_root):
		path = pathlib.Path(f'{pallet_root}/.treeinfo')
		if not path.is_file():
			return []

		lines = path.read_text().splitlines()

		name, version, release, arch, distro_family = [None] * 5

		for line in lines:
			kv = line.split('=')
			if len(kv) != 2:
				continue

			key, value = kv[0].strip(), kv[1].strip()

			if key == 'family':
				if value.startswith('CentOS'):
					name = 'CentOS'
					distro_family = 'redhat'
				elif value.startswith('Oracle'):
					name = 'OLE'
					distro_family = 'redhat'

			elif key == 'version':
				version = value.split('.')[0]
			elif key == 'arch':
				arch = value

		if not name:
			return []

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

		p = PalletInfo(name, version, release, arch, distro_family, pallet_root, self.__class__.__name__)
		return [p] if p.is_complete() else []
