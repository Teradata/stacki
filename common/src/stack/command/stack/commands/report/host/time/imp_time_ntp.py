#
# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#

import stack.commands


class Implementation(stack.commands.Implementation):	
	"""
	Output /etc/ntp.conf
	"""

	def client(self, host, timeserver):
		#
		# configure NTP to use an external server
		#
		self.owner.addOutput(host, '<stack:file stack:name="/etc/ntp.conf">')
		self.owner.addOutput(host, 'server %s' % timeserver)
		self.owner.addOutput(host, 'driftfile /var/lib/ntp/drift')
		self.owner.addOutput(host, '</stack:file>')

		#
		# force the clock to be set on next boot
		#
		self.owner.addOutput(host, 'mkdir -p /etc/ntp')
		self.owner.addOutput(host, '<stack:file stack:name="/etc/ntp/step-tickers">')
		self.owner.addOutput(host, '%s' % timeserver)
		self.owner.addOutput(host, '</stack:file>')


	def server(self, host, timeserver):
		self.owner.addOutput(host, '<stack:file stack:name="/etc/ntp.conf">')
		self.owner.addOutput(host, 'server %s iburst' % timeserver)
		self.owner.addOutput(host, 'server 127.127.1.1 iburst')
		self.owner.addOutput(host, 'fudge 127.127.1.1 stratum 10')
		self.owner.addOutput(host, 'driftfile /var/lib/ntp/drift')
		self.owner.addOutput(host, '</stack:file>')


	def run(self, args):
		(host, appliance, timeserver) = args

		self.owner.addOutput(host, '/sbin/chkconfig ntpd on')
		self.owner.addOutput(host, '/sbin/chkconfig chronyd off')

		self.owner.addOutput(host,
			'<stack:file stack:name="/etc/cron.hourly/ntp" stack:perms="0755">')
		self.owner.addOutput(host, '#!/bin/sh')
		self.owner.addOutput(host, 'if ! ( /usr/sbin/ntpq -pn 2&gt; /dev/null | grep -e \'^\*\' &gt; /dev/null ); then')
		self.owner.addOutput(host, '    /etc/rc.d/init.d/ntpd restart &gt; /dev/null 2&gt;&amp;1')
		self.owner.addOutput(host, 'fi')
		self.owner.addOutput(host, '</stack:file>')

		self.owner.addOutput(host, '<stack:file stack:name="/etc/sysconfig/ntpd">')
		self.owner.addOutput(host,
			'OPTIONS="-A -u ntp:ntp -p /var/run/ntpd.pid"')
		self.owner.addOutput(host, '</stack:file>')

		if appliance == 'frontend':
			self.server(host, timeserver)
		else:
			self.client(host, timeserver)

		#
		# set the clock right now
		#
		self.owner.addOutput(host, '/usr/sbin/ntpdate %s' % timeserver)

