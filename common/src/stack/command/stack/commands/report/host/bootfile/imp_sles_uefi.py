#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@
#

import stack.commands
from stack.exception import *

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

os_template = """search.fs_label BOOTEFI root
chainloader ($root)/efi/SuSE/elilo.efi
boot
"""

class Implementation(stack.commands.Implementation):
	def run(self, h):
		host     = h['host']
		ip       = h['ip']
		mask     = h['mask']
		gateway  = h['gateway']
		kernel   = h['kernel']
		ramdisk  = h['ramdisk']
		args     = h['args']
		filename = h['filename']
		attrs    = h['attrs']
		action   = h['action']
		boottype = h['type']

		# Get the bootaction for the host (install or os) and
		# lookup the actual kernel, ramdisk, and args for the
		# specific action.
		if boottype == 'os':
			self.owner.addOutput(host, os_template)
		else:
			args = "%s BOOTIF=00:$net_default_mac" % args
			self.owner.addOutput(host, install_template % (kernel, kernel, args, ramdisk, ramdisk))
