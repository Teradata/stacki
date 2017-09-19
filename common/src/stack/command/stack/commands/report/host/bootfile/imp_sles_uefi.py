# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


install_template = """set gfxpayload=keep
insmod gzio
insmod part_gpt
insmod ext2

set timeout=5

menuentry "Stacki UEFI Install" {
	echo "Loading %s"
	linuxefi /%s %s
	echo "Loading %s"
	initrdefi /%s
}
"""

sles11_os_template = """search.fs_label BOOTEFI root
chainloader ($root)/efi/SuSE/elilo.efi
boot
"""

sles12_os_template = """search.fs_label BOOTEFI root
configfile ($root)/efi/sles/grub.cfg
boot
"""


class Implementation(stack.commands.Implementation):
	def run(self, h):
		host	 = h['host']
		ip	 = h['ip']
		mask	 = h['mask']
		gateway	 = h['gateway']
		kernel	 = h['kernel']
		ramdisk	 = h['ramdisk']
		args	 = h['args']
		filename = h['filename']
		attrs	 = h['attrs']
		action	 = h['action']
		boottype = h['type']


		# Get pallets for Host
		pallets = self.owner.getHostAttr(h['host'], 'pallets')
		os_template = sles11_os_template
		for p in pallets:
			if p.startswith('SLES-12'):
				os_template = sles12_os_template
				break

		# Get the bootaction for the host (install or os) and
		# lookup the actual kernel, ramdisk, and args for the
		# specific action.
		if boottype == 'os':
			self.owner.addOutput(host, os_template)
		else:
			args = "%s BOOTIF=00:$net_default_mac" % args
			self.owner.addOutput(host, install_template % (kernel, kernel, args, ramdisk, ramdisk))
