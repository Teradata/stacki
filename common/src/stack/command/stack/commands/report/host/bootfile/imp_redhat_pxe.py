# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import sys
import re

class Implementation(stack.commands.Implementation):

	def run(self,h):
		for hi in h['interfaces']:
			self.createPxe(h,hi)

	def createPxe(self, h, hi):
		host     = h['host']
		ip       = hi['ip']
		mask     = hi['mask']
		gateway  = hi['gateway']
		iface 	 = hi['interface']
		kernel   = h['kernel']
		ramdisk  = h['ramdisk']
		args     = h['args']
		attrs    = h['attrs']
		boottype = h['type']
		dnsserver  = attrs.get('Kickstart_PrivateDNSServers')
		nextserver = attrs.get('Kickstart_PrivateKickstartHost')

		# rewrite parts of the bootaction
		if args:
			sargs = args.split()

		if gateway != nextserver:
		# If the ksdevice= is set fill in the network
		# information as well.  This will avoid the DHCP
		# request inside anaconda.
			r = re.compile('inst.ks=http.*')
			sarg = [ sargs.index(x) for x in sargs if r.match(x)]
			if sarg != []:
				# This may not be strictly necessary, but doing it means less
				# confusion, unless they look at their bootaction, in which
				# case this will be really confusing.
				sargs[sarg[0]] = 'inst.ks=https://%s/install/sbin/profile.cgi' % gateway

		r = re.compile('ksdevice=.*')
		sarg = [ sargs.index(x) for x in sargs if r.match(x)]
		if sarg != []:
			sargs[sarg[0]] = 'ksdevice=%s' % iface
			args = ' '.join(sargs)
			args += ' ip=%s gateway=%s netmask=%s dns=%s nextserver=%s' % \
				(ip, gateway, mask, gateway, gateway)
		else:
			args = ' '.join(sargs)

		self.owner.addOutput(host, 'default stack')
		self.owner.addOutput(host, 'prompt 0')
		self.owner.addOutput(host, 'label stack')

		if kernel:
			if kernel[0:7] == 'vmlinuz':
				self.owner.addOutput(host, '\tkernel %s' % (kernel))
			else:
				self.owner.addOutput(host, '\t%s' % (kernel))
		if ramdisk and len(ramdisk) > 0:
			if len(args) > 0:
				args += ' initrd=%s' % ramdisk
			else:
				args = 'initrd=%s' % ramdisk

		if args and len(args) > 0:
			self.owner.addOutput(host, '\tappend %s' % args)

		if boottype == "install":
			self.owner.addOutput(host, '\tipappend 2')
