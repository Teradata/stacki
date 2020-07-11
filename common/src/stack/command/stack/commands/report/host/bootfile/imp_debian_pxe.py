# @copyright@
# @copyright@

import os
import stack.commands
from .imp_base import PXEImplementation

class Implementation(PXEImplementation):

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
		mac       = i['mac']
		mask      = i['mask']
		gateway   = i['gateway']

		arch = 'amd64' # TODO - support multiple archs
		
		dnsserver  = attrs.get('Kickstart_PrivateDNSServers')
		nextserver = attrs.get('Kickstart_PrivateKickstartHost')

		self.owner.addOutput(host, self.get_sux_header(os.path.join(os.path.sep,
									    'tftpboot',
									    'debian',
									    'debian-installer',
									    arch,
									    'pxelinux.cfg',
									    self.get_tftpboot_filename(mac))))
		self.owner.addOutput(host, 'default stack')
		self.owner.addOutput(host, 'prompt 0')
		self.owner.addOutput(host, 'label stack')

		if kernel:
			if kernel.endswith('linux'):
				self.owner.addOutput(host, f'\tkernel {kernel}')
			else:
				self.owner.addOutput(host, f'\t{kernel}')

		if args is None:
			args = ''
			
		if ramdisk and len(ramdisk) > 0:
			args += f' initrd={ramdisk}'

		if args and len(args) > 0:
			self.owner.addOutput(host, f'\tappend {args}')

		self.owner.addOutput(host, self.get_sux_trailer())
