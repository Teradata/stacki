# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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

os_template = {
	'sles11.x': """search.fs_label BOOTEFI root
chainloader ($root)/efi/SuSE/elilo.efi
boot
""",
	'sles12.x': """search.fs_label BOOTEFI root
configfile ($root)/efi/sles/grub.cfg
boot
""",
	'redhat7.x': """search.fs_uuid %s root
configfile ($root)/efi/centos/grub.cfg
""",
}

class Implementation(stack.commands.Implementation):

	def run(self, args):
		h = args[0]
		i = args[1]

		host      = h['host']
		kernel    = h['kernel']
		ramdisk   = h['ramdisk']
		args      = h['args']
		attrs     = h['attrs']
		boottype  = h['type']

		interface = i['interface']
		ip        = i['ip']
		mask      = i['mask']
		gateway   = i['gateway']


		# get distro and version
		distro_version = f"{attrs.get('os')}{attrs.get('os.version')}"

		root_uuid = None
		if boottype == 'os' and attrs.get('os') == 'redhat':
			for part in self.owner.call('list.host.partition', [host]):
				if part['mountpoint'] == '/boot/efi':
					root_uuid = part['uuid']
					break
			if root_uuid:
				self.owner.addOutput(host, os_template[distro_version] % root_uuid)
		# Get the bootaction for the host (install or os) and
		# lookup the actual kernel, ramdisk, and args for the
		# specific action.
		elif boottype == 'os':
			self.owner.addOutput(host, os_template[distro_version])
		else:
			args = "%s BOOTIF=00:$net_default_mac" % args
			self.owner.addOutput(host, install_template % (kernel, kernel, args, ramdisk, ramdisk))
