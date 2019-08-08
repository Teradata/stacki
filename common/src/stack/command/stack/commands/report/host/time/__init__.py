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
# The timekeeping system set up by default in Stacki has the
# following design considerations.
#
# 1. All servers in the cluster, can sync times from 2 sources. Any external server
#    specified in the time.servers attribute, and any servers with time.orphantype value
#    set to "parent"
# 2. By default, the frontend is configured as a parent, and can serve time to the rest
#    of the cluster.
# 3. time.servers attribute should ideally be set for the frontend, so that it can pick
#    up
# 4. If the time.servers attribute is set for a backend host,
#    then those servers are appended to the list of servers to
#    sync from.
# 5. If certain nodes are set as parent servers, they can form a time island, from which
#    all other servers can sync
# 6. If Stacki shouldn't be managing time at all, then the time.protocol attribute can
#    be unset, and the admin can manage the time by themselves

class Command(stack.commands.HostArgumentProcessor,
	stack.commands.NetworkArgumentProcessor,
	stack.commands.report.command):
	"""
	Create a time configuration report (NTP or chrony).
	At a minimum at least one server in the cluster has to be designated as a "parent"
	time server. This ensures that there's atleast one server in the cluster that can
	serve time. By default, the stacki frontend is a parent timekeeper.
	Ideally, a "parent" time server will also have the "time.servers" attribute set
	to talk to an external time server, so that the cluster is in sync with the external
	time-keeping entity.

	Relevant Attributes:

	time.servers -	Optional - Comma-separated list of servers (IP addresses
			or resolvable names) that dictate the servers to use for time-keeping.
			This list is in *addition* to the Stacki frontend.

	time.orphantype - Required for at-least one host in the cluster.
			Only the value of "parent" affects the behaviour
			of the NTP service. If a host is designated as a
			parent Orphan-type, that means this host can
			co-ordinate time with other peers to maintain
			time on the time island.

	time.protocol - Optional - Can take the value of "chrony" or "ntp". Default
			Stacki behaviour is to use chrony for all hosts, except SLES 11 hosts.
			SLES 11 hosts use NTP by default

	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>
	
	<example cmd='report host time backend-0-0'>
	Create a time configuration file for backend-0-0.

	*Configuration*
	Scenario 1: Use Frontend for time keeping
	If the desired behavior is to use the frontend as the primary, and only time server,
	no configuration changes have to be made in Stacki. This is the default behavior.

	Scenario 2: Use frontend for time keeping, in sync with an external time server.
	Set time.servers attribute on the frontend to the IP Address, or Hostname of an external time server.
	This will set the frontend to sync time against an external time server, and all other hosts to
	sync time from the frontend.

	Scenario 3: Sync time on all hosts using an external time server only.
	Unset the frontend appliance attribute of time.orphantype. This will disable the frontend
	from serving time.
	Set the time.servers attribute for all hosts to the IP address, or Hostname of external
	time server. This will require that all hosts can contact, and connect to the external time
	server.

	Scenario 4: Sync time on some hosts from external time servers, and create a time island.
	Set some of the hosts' time.orphantype attribute to parent. Then set those hosts' time.servers
	attribute to the IP address, or Hostname of external time server. The list of parent time servers
	can include the frontend or not.

	Scenario 5: Don't use Stacki to sync time.
	To do this, make sure that the time.protocol attribute is not set for a host or a set of hosts.
	</example>
	"""

	def getNTPPeers(self, host):
		
		peerlist = []
		parents = [ h for h in self.attrs if ( self.attrs[h].get('time.orphantype') == 'parent' and h != host) ]
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
					raise CommandError(self, f"Network {net} is unknown to Stacki\n" + \
						"Fix 'time.networks' attribute for host {host}")
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

		if not timeservers:
			timeservers = []

		for peer in self.getNTPPeers(host):
			timeservers.append(peer)
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

			if protocol == None:
				continue

			if self.osversion == '11.x':
				protocol = 'ntp'

			self.timeservers = self.getNTPServers(host)
			if len(self.timeservers) == 0:
				if not 'time.orphantype' in self.attrs[host] or not self.attrs[host]['time.orphantype'] == 'parent':
					raise CommandError(self, f'No time servers specified for host {host}\n' +
						'Check time.* attributes, and network interface assignments')

			self.runImplementation('time_%s' % protocol, (host))

			self.set_timezone(host)

		self.endOutput(padChar='', trimOwner=True)
