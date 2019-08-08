#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
import stack.text

class Implementation(stack.commands.Implementation):	
	"""
	Output /etc/chrony.conf
	"""

	def client(self, host):
		self.owner.addOutput(host, '<stack:file stack:name="/etc/chrony.conf">')
		self.owner.addOutput(host, stack.text.DoNotEdit())

		self.owner.addOutput(host, "# NTP/Chrony Servers to Sync from.")
		for server in self.owner.timeservers:
			self.owner.addOutput(host, f'server {server} iburst')

		self.owner.addOutput(host, "\n# Allow NTP client access")
		for network in self.owner.getNTPNetworks(host):
			self.owner.addOutput(host, f'allow {network}')

		self.owner.addOutput(host, "\n# Allow this system to run in Orphan mode with a Stratum of 10")
		self.owner.addOutput(host, 'local stratum 10 orphan\n')

		# If NTP Orphan type is set to parent, allow this system to
		# serve NTP information
		orphantype = self.owner.attrs[host].get('time.orphantype')
		if orphantype == 'parent':
			self.owner.addOutput(host, '# NTP / Chrony Peers')
			for peer in self.owner.getNTPPeers(host):
				self.owner.addOutput(host, f'peer {peer}')
		else:
			# Get all the NTP peers in the cluster
			self.owner.addOutput(host, '\n# Time Island NTP Parent Servers')
			for peer in self.owner.getNTPPeers(host):
				self.owner.addOutput(host, f"server {peer}")

		self.owner.addOutput(host, "\n# Drift File")
		self.owner.addOutput(host, 'driftfile /var/lib/chrony/drift\n')

		self.owner.addOutput(host, "# Logging Information")
		self.owner.addOutput(host, 'logdir /var/log/chrony')
		self.owner.addOutput(host, 'log measurements statistics tracking')
		self.owner.addOutput(host, '</stack:file>')


	def server(self, host):

		self.owner.addOutput(host, '<stack:file stack:name="/etc/chrony.conf">')
		self.owner.addOutput(host, stack.text.DoNotEdit())

		self.owner.addOutput(host, "# NTP/Chrony Servers to Sync from.")
		for server in self.owner.timeservers:
			self.owner.addOutput(host, f'server {server} iburst')

		self.owner.addOutput(host, "\n# Set local Stratum to 10.")
		self.owner.addOutput(host, 'local stratum 10')
		self.owner.addOutput(host, 'stratumweight 0\n')

		self.owner.addOutput(host, "# Drift File")
		self.owner.addOutput(host, 'driftfile /var/lib/chrony/drift\n')

		self.owner.addOutput(host, "# Periodically sync system time to Hardware RTC")
		self.owner.addOutput(host, 'rtcsync\n')

		self.owner.addOutput(host, "\n# Allow NTP client access")
		for network in self.owner.getNTPNetworks(host):
			self.owner.addOutput(host, f'allow {network}')

		self.owner.addOutput(host, "\n# Allow Chronyd configuration from localhost only")
		self.owner.addOutput(host, 'bindcmdaddress 127.0.0.1')
		self.owner.addOutput(host, 'bindcmdaddress ::1')

		self.owner.addOutput(host, "\n# Logging Information")
		self.owner.addOutput(host, 'logchange 0.5')
		self.owner.addOutput(host, 'logdir /var/log/chrony')
		self.owner.addOutput(host, 'log measurements statistics tracking')
		self.owner.addOutput(host, '</stack:file>')


	def run(self, host):

		self.owner.addOutput(host, "systemctl stop chronyd")
		if self.owner.appliance == "frontend":
			self.server(host)
		else:
			self.client(host)

		if self.owner.timeservers:
			self.owner.addOutput(host, "/usr/sbin/chronyd -q 'server %s iburst'" % self.owner.timeservers[0])

		self.owner.addOutput(host, "systemctl enable chronyd")
		self.owner.addOutput(host, 'systemctl start chronyd')
