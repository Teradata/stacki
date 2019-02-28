#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
import stack.text
import ipaddress
from stack.exception import *

## DESIGN CONSIDERATIONS
# The NTP system set up by default in Stacki has the
# following design considerations.
#
# 1. The Frontend syncs its own time from external servers. - stored in time.servers attribute
# 2. The Frontend serves NTP to all backends on all networks that are PXE enabled.
# 3. By default, the Backends sync time from the frontend.
# 4. If the time.servers attribute is set for a backend host,
#    then those servers are appended to the list of servers to
#    sync from.
# 5. If certain nodes are set as parent servers, they can form a time island, from which
#    all other servers can sync

class Command(stack.commands.HostArgumentProcessor,
	stack.commands.NetworkArgumentProcessor,
	stack.commands.report.command):
	"""
	Create a time configuration report (NTP or chrony).

	Relevant Attributes:

	time.servers -	Optional - Comma-separated list of servers (IP addresses
			or resolvable names) that dictate the servers to use for time-keeping.
			This list is in *addition* to the Stacki frontend.

	time.orphantype - Optional - Only the value of "parent" affects the behaviour
			if the NTP service. If a host is designated as a parent Orphan-type,
			that means this host can co-ordinate time with other peers to maintain
			time on the time island.

	time.protocol - Optional - Can take the value of "chrony" or "ntp". Default
			Stacki behaviour is to use chrony for the hosts.

	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>
	
	<example cmd='report host time backend-0-0'>
	Create a time configuration file for backend-0-0.
	</example>
	"""

	def getNTPPeers(self, host):
		
		peerlist = []
		parents = [ h for h in self.attrs if ( self.attrs[h].get('time.orphantype') == 'parent' and h != host and h != self.frontend ) ]
		if parents:
			op = self.call('list.host.interface', parents + ['expanded=true'])
			networks = self.getNTPNetworkNames(host)
			n = [ intf['ip'] for intf in op if intf['network'] in networks ]
			n.sort()
			for i in n:
				if i not in peerlist:
					peerlist.append(i)
		return peerlist

	def getNTPNetworkNames(self, host):
		networks = []
		output = self.call('list.host.interface', [ host , 'expanded=true'])
		for o in output:
			if o['pxe'] == True:
				networks.append(o['network'])
		# If there are any extra ntp networks defined for the node,
		# they would be specified in the attribute "ntp.networks",
		# and is a comma separated list of "networks" that Stacki
		# knows about.
		stacki_networks = self.getNetworkNames()
		ntp_net_extra = self.attrs[host].get('time.networks')
		if ntp_net_extra:
			for net in ntp_net_extra.split(','):
				if net not in stacki_networks:
					raise CommandError(self, f"Network {net} is unknown to Stacki. Fix 'time.networks' attribute for host {host}")
				networks.append(net)
		return networks

	def getNTPNetworks(self, host):
		n = self.getNTPNetworkNames(host)
		networks = []
		if n:
			output = self.call('list.network', n)
			for o in output:
				address = o['address']
				mask = o['mask']
				ipnetwork = ipaddress.IPv4Network(str(address + '/' + mask))
				networks.append(ipnetwork)
		return networks

	def getNTPServers(self, host):
		timeservers = self.attrs[host].get('time.servers')
		if timeservers:
			timeservers = timeservers.split(",")

		if self.appliance == 'frontend':
			if not timeservers:
				timeservers = [self.attrs[host].get('Kickstart_PublicNTPHost')]
		else:
			n = []
			output = self.call('list.host.interface', [ host , 'expanded=true'])
			for o in output:
				if o['network'] in self.frontend_ntp_addrs:
					n.append(self.frontend_ntp_addrs[o['network']])
			if not timeservers:
				timeservers = n
			else:
				timeservers = n + timeservers

		return timeservers

	def set_timezone(self, host):
		tz = self.attrs[host].get('Kickstart_Timezone')
		if not tz:
			tz = 'UTC'
		self.addOutput(host, '<stack:file stack:name="/etc/sysconfig/clock" stack:perms="0644">')
		self.addOutput(host, stack.text.DoNotEdit())
		self.addOutput(host, "# Hardware clock is set to UTC")
		self.addOutput(host, 'HWCLOCK="-u"\n')
		self.addOutput(host, "# Sync System clock to Hardware Clock")
		self.addOutput(host, 'SYSTOHC="yes"\n')
		self.addOutput(host, "# Timezone for the system")
		self.addOutput(host, f'TIMEZONE="{tz}"\n')
		self.addOutput(host, "# Default timezone")
		self.addOutput(host, f'DEFAULT_TIMEZONE="{tz}"\n')
		self.addOutput(host, '</stack:file>')
		self.addOutput(host, f"zic -l {tz}")

	def run(self, params, args):
		self.beginOutput()

		hosts = self.getHostnames(args)

		self.frontend = self.getHostnames(['a:frontend'])[0]

		# Get all host(s) attributes
		self.attrs = {}
		for row in self.call('list.host.attr'):
			host = row['host']
			if host not in self.attrs:
				self.attrs[host] = {}
			self.attrs[host][row['attr']] = row['value']

		# Get all IP addresses on which the frontend serves PXE. This
		# is a good default set of IP addresses to serve from.
		self.frontend_ntp_addrs = {}
		for intf in self.call("list.host.interface",["a:frontend", "expanded=true"]):
			if intf["pxe"] == True:
				self.frontend_ntp_addrs[intf['network']] = intf['ip']

		for host in hosts:
			protocol   = self.attrs[host].get('time.protocol')
			self.appliance  = self.attrs[host].get('appliance')
			self.osversion  = self.attrs[host].get('os.version')

			if self.osversion == '11.x':
				protocol = 'ntp'

			self.timeservers = self.getNTPServers(host)

			self.runImplementation('time_%s' % protocol, (host))

			self.set_timezone(host)

		self.endOutput(padChar='', trimOwner=True)
