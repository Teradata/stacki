#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands

NTP_CRON = """<stack:file stack:name="/etc/cron.hourly/ntp" stack:perms="0755">
#!/bin/sh

if ! ( /usr/sbin/ntpq -pn 2&gt; /dev/null | grep -e \'^\*\' &gt; /dev/null ); then
	/etc/rc.d/init.d/ntpd restart &gt; /dev/null 2&gt;&amp;1'
fi
</stack:file>
"""


class Implementation(stack.commands.Implementation):	
	"""
	Output NTP Configuration
	"""

	def client(self, host):
		#
		# configure NTP to use an external server
		#
		self.owner.addOutput(host, '<stack:file stack:name="/etc/ntp.conf">')
		self.owner.addOutput(host, stack.text.DoNotEdit())
		self.owner.addOutput(host, "\n# Logging Information")
		self.owner.addOutput(host, "logfile /var/log/ntp")

		self.owner.addOutput(host, "\n# Drift File")
		self.owner.addOutput(host, 'driftfile /var/lib/ntp/drift')

		self.owner.addOutput(host, "\n# NTP Auth Info")
		self.owner.addOutput(host, 'keys /etc/ntp.keys')
		self.owner.addOutput(host, 'trustedkey 1')
		self.owner.addOutput(host, 'requestkey 1')
		self.owner.addOutput(host, 'controlkey 1')

		self.owner.addOutput(host, "\n# Disable Panic for any clock offset")
		self.owner.addOutput(host, 'tinker panic 0')

		self.owner.addOutput(host, "\n# Allow this system to run in Orphan mode with a Stratum of 10")
		self.owner.addOutput(host, 'tos orphan 10')

		self.owner.addOutput(host, "\n# Accept broadcast NTP information")
		self.owner.addOutput(host, 'broadcastclient')

		self.owner.addOutput(host, "\n# Pull time from the following servers")
		for server in self.owner.timeservers:
			self.owner.addOutput(host, f"server {server}")

		self.owner.addOutput(host, "\n# Allow time from the following servers to modify config")
		for server in self.owner.timeservers:
			self.owner.addOutput(host, f"restrict {server}")

		for network in self.owner.getNTPNetworks(host):
			self.owner.addOutput(host, f"\n# Allow servers from the {network.network_address}/{network.prefixlen} network to modify config")
			self.owner.addOutput(host, f"restrict {network.network_address} mask {network.netmask}")

		# If NTP Orphan type is set to parent, allow this system to
		# serve NTP information
		orphantype = self.owner.attrs[host].get('time.orphantype')
		if orphantype == 'parent':
			self.owner.addOutput(host, '# NTP / Chrony Peers')
			for peer in self.owner.getNTPPeers(host):
				self.owner.addOutput(host, f'peer {peer}')
			for network in self.owner.getNTPNetworks(host):
				self.owner.addOutput(host, f"# Broadcast NTP over the {network.network_address}/{network.prefixlen} network")
				self.owner.addOutput(host, f"broadcast {network.broadcast_address} key 1")

		else:
			# Get all the NTP peers in the cluster
			self.owner.addOutput(host, '\n# Time Island NTP Parent Servers')
			for peer in self.owner.getNTPPeers(host):
				self.owner.addOutput(host, f"server {peer}")

		self.owner.addOutput(host, '</stack:file>')

		#
		# force the clock to be set on next boot
		#
		self.owner.addOutput(host, '<stack:file stack:name="/etc/ntp/step-tickers">')
		for server in self.owner.timeservers:
			self.owner.addOutput(host, server)
		self.owner.addOutput(host, '</stack:file>')


	def server(self, host):
		self.owner.addOutput(host, '<stack:file stack:name="/etc/ntp.conf">')
		for server in self.owner.timeservers:
			self.owner.addOutput(host, f"server {server} iburst")
		self.owner.addOutput(host, 'server 127.127.1.1 iburst')
		self.owner.addOutput(host, 'fudge 127.127.1.1 stratum 10')
		self.owner.addOutput(host, 'driftfile /var/lib/ntp/drift')
		self.owner.addOutput(host, '</stack:file>')


	def run(self, host):

		if self.owner.osversion == '11.x':
			self.owner.addOutput(host, f'/sbin/chkconfig ntp on')
			self.owner.addOutput(host, 'service ntp stop')
		else:
			self.owner.addOutput(host, 'systemctl enable ntpd')
			self.owner.addOutput(host, 'systemctl disable chronyd')
			self.owner.addOutput(host, 'systemctl stop ntpd')

		self.owner.addOutput(host, NTP_CRON)

		self.owner.addOutput(host, '<stack:file stack:name="/etc/sysconfig/ntpd">')
		self.owner.addOutput(host,
			'OPTIONS="-A -u ntp:ntp -p /var/run/ntpd.pid"')
		self.owner.addOutput(host, '</stack:file>')

		if self.owner.appliance == 'frontend':
			self.server(host)
		else:
			self.client(host)

		#
		# set the clock right now
		#
		if self.owner.timeservers:
			self.owner.addOutput(host, '/usr/sbin/ntpdate %s' % self.owner.timeservers[0])
		# Restart the NTPD service
		if self.owner.osversion == '11.x':
			self.owner.addOutput(host, 'service ntp start')
		else:
			self.owner.addOutput(host, 'systemctl start ntpd')
