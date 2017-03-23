#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@
#

import stack.commands
from stack.exception import *

class Implementation(stack.commands.Implementation):
	def run(self, args):
		host = args[0]
		action = args[1]

		# Get the bootaction for the host (install or os) and
		# lookup the actual kernel, ramdisk, and args for the
		# specific action.
		kernel, ramdisk, args = self.owner.getBootParams(host, action)

		# If the ksdevice= is set fill in the network
		# information as well.  This will avoid the DHCP
		# request inside anaconda.

		if args and args.find('ksdevice=') != -1:
			for row in self.owner.call('list.host.interface', [host, 'expanded=True']):
				if row['ip'] and row['pxe']:
					ip = row['ip']
					gateway = row['gateway']
					netmask = row['mask']
					args += ' ip=%s gateway=%s netmask=%s' % (ip, gateway, netmask) 
			dnsserver = self.owner.getHostAttr(host,
				'Kickstart_PrivateDNSServers')
			nextserver = self.owner.getHostAttr(host,
				'Kickstart_PrivateKickstartHost')
			args += ' dns=%s nextserver=%s' % \
				(dnsserver, nextserver)

		self.owner.addOutput(host,'default stack')
		self.owner.addOutput(host,'prompt 0')
		self.owner.addOutput(host,'label stack')

		if kernel:
			if kernel[0:7] == 'vmlinuz':
				self.owner.addOutput(host,'\tkernel %s' % (kernel))
			else:
				self.owner.addOutput(host,'\t%s' % (kernel))
		if ramdisk and len(ramdisk) > 0:
			if len(args) > 0:
				args += ' initrd=%s' % ramdisk
			else:
				args = 'initrd=%s' % ramdisk

		if args and len(args) > 0:
			self.owner.addOutput(host,'\tappend %s' % args)

		if action == "install":
			self.owner.addOutput(host,'\tipappend 2')
