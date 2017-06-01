#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@
#

import stack.commands
from stack.exception import *

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
		action	 = h['action']

                dnsserver  = attrs.get('Kickstart_PrivateDNSServers')
                nextserver = attrs.get('Kickstart_PrivateKickstartHost')


		# If the ksdevice= is set fill in the network
		# information as well.  This will avoid the DHCP
		# request inside anaconda.

		if args and args.find('ksdevice=') != -1:
			args += ' ip=%s gateway=%s netmask=%s dns=%s nextserver=%s' % \
				(ip, gateway, mask, dnsserver, nextserver)

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
