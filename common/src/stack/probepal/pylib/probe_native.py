import pathlib
import xml.etree.ElementTree as ET

from stack.probepal.common import PalletInfo, Probe

class NativePalletProbe(Probe):
	'''
	This prober is intended to look for and parse one or more roll-*.xml files which indicates a stacki native pallet.

	Note that a native pallet may actually contain multiple pallets (this is referred to as a Jumbo Pallet), with a roll-*.xml file for each.

	The contents of such a file look like this:

	<roll name="stacki" interface="6.0.2">
	<timestamp time="16:10:04" date="March 20 2019" tz="UTC"/>
	<color edge="" node=""/>
	<info version="05.02.06.03" release="sles12" arch="x86_64" os="sles"/>
	<iso maxsize="0" addcomps="0" bootable="0" mkisofs="-b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table"/>
	<rpm rolls="0" bin="1" src="0"/>
	<author name="root" host="localhost"/>
	<gitstatus><![CDATA[
	On branch support/05.02.06.03
	]]></gitstatus>
	<gitlog>
	b3d353f21f0f29e212138bc02b5154388f0d1d26
	</gitlog>
	</roll>
	'''


	def __init__(self, weight=10, desc='roll.xml files - native stacki'):
		super().__init__(weight=weight, desc=desc)

	def probe(self, pallet_root):
		roll_files = list(pathlib.Path(pallet_root).glob('**/roll-*.xml'))

		if not roll_files:
			return []

		# to support jumbo pallets, this probe must return a list of palletinfo objects
		# if even one roll-*.xml file fails to parse, we fail the whole pallet
		pal_infos = []

		for fi in roll_files:
			if not fi.is_file():
				return []

			real_root = str(fi.parent)

			name, version, release, arch, distro_family = [None] * 5
			try:
				docroot = ET.parse(fi).getroot()
				name = docroot.attrib['name']
				info = docroot.find('info')
				version = info.attrib['version']
				release = info.attrib['release']
				arch = info.attrib['arch']
				distro_family = info.attrib['os']
			except Exception:
				# any errors, just fail and move to the next probe
				return []

			p = PalletInfo(name, version, release, arch, distro_family, real_root)
			if not p.is_complete():
				return []
			pal_infos.append(p)

		return pal_infos
