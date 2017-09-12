#
# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#

import ipaddress
import os
import stack.commands

class Implementation(stack.commands.Implementation):	
	"""
	Output /etc/chrony.conf
	"""

	def client(self, host, timeserver):
		self.owner.addOutput(host, '<stack:file stack:name="/etc/chrony.conf">')
		self.owner.addOutput(host, 'server %s' % timeserver)
		self.owner.addOutput(host, 'allow %s' % timeserver)
		self.owner.addOutput(host, 'local stratum 10')
		self.owner.addOutput(host, 'driftfile /var/lib/chrony/drift')
		self.owner.addOutput(host, 'logdir /var/log/chrony')
		self.owner.addOutput(host, 'log measurements statistics tracking')
		self.owner.addOutput(host, '</stack:file>')


	def server(self, host, timeserver):
		network = None
		output = self.owner.call('list.host.interface', [ host ])
		for o in output:
			if o['default']:
				network = o['network']
				break
		if not network:
			return

		address = None
		mask = None
		output = self.owner.call('list.network', [ network ])
		for o in output:
			address = o['address']
			mask = o['mask']
		if not address or not mask:
			return

		ipnetwork = ipaddress.IPv4Network(str(address + '/' + mask))

		self.owner.addOutput(host, '<stack:file stack:name="/etc/chrony.conf">')
		self.owner.addOutput(host, 'server %s iburst' % timeserver)
		self.owner.addOutput(host, 'local stratum 10')
		self.owner.addOutput(host, 'stratumweight 0')
		self.owner.addOutput(host, 'driftfile /var/lib/chrony/drift')
		self.owner.addOutput(host, 'rtcsync')
		self.owner.addOutput(host, 'allow %s/%s' % (address, ipnetwork.prefixlen))
		self.owner.addOutput(host, 'bindcmdaddress 127.0.0.1')
		self.owner.addOutput(host, 'bindcmdaddress ::1')
		self.owner.addOutput(host, 'logchange 0.5')
		self.owner.addOutput(host, 'logdir /var/log/chrony')
		self.owner.addOutput(host, 'log measurements statistics tracking')
		self.owner.addOutput(host, '</stack:file>')


	def run(self, args):
		(host, appliance, timeserver) = args

		self.owner.addOutput(host, "kill `pidof chronyd`")

		self.owner.addOutput(host, '/sbin/chkconfig chronyd on')
		self.owner.addOutput(host, '/sbin/chkconfig ntp off')

		if appliance == 'frontend':
			self.server(host, timeserver)
		else:
			self.client(host, timeserver)

		#
		# set the time right now
		#
		self.owner.addOutput(host, 'pidof chronyd')
		self.owner.addOutput(host, 'while [ $? -eq 0 ]')
		self.owner.addOutput(host, 'do')
		self.owner.addOutput(host, '\tsleep 1')
		self.owner.addOutput(host, '\tkill -9 `pidof chronyd`')
		self.owner.addOutput(host, '\tpidof chronyd')
		self.owner.addOutput(host, 'done')

		self.owner.addOutput(host,
			"/usr/sbin/chronyd -q 'server %s iburst'" % timeserver)

