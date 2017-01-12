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
		filename = args[2]
		ip = args[3]
		netmask = args[4]
		gateway = args[5]

		# Get the bootaction for the host (install or os) and
		# lookup the actual kernel, ramdisk, and args for the
		# specific action.

		for row in self.owner.call('list.host', [ host ]):
			if action == 'install':
				bootaction = row['installaction']
			else:
				bootaction = row['runaction']

		kernel = ramdisk = args = None
		for row in self.owner.call('list.bootaction'):
			if row['action'] == bootaction:
				kernel  = row['kernel']
				ramdisk = row['ramdisk']
				args    = row['args']

		# If the ksdevice= is set fill in the network
		# information as well.  This will avoid the DHCP
		# request inside anaconda.

		if args and args.find('ksdevice=') != -1:
			dnsserver = self.owner.db.getHostAttr(host,
				'Kickstart_PrivateDNSServers')
			nextserver = self.owner.db.getHostAttr(host,
				'Kickstart_PrivateKickstartHost')
			
			args += ' ip=%s gateway=%s netmask=%s dns=%s nextserver=%s' % \
				(ip, gateway, netmask, dnsserver, nextserver)

		self.owner.addOutput(host, '<stack:file stack:name="%s" stack:owner="root:apache" stack:perms="0664" stack:rcs="off"><![CDATA[' % filename)
		self.owner.addOutput(host, 'default stack')
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

		# If using ksdevice=bootif we need to
		# pass the PXE information to loader.
		
		if args and args.find('bootif') != -1:
			self.owner.addOutput(host,'\tipappend 2')


		self.owner.addOutput(host, ']]></stack:file>')

