# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.report.host.command):
	"""
	Generate the /etc/resolv.conf for a host

	<arg optional='0' repeat='1' type='string' name='host'>
	Host name of machine
	</arg>
	"""

	def outputResolv(self, host):
		zones = {}
		dns = {}	

		for row in self.call('list.network'):
			zones[row['network']] = row['zone']
			dns[row['network']] = row['dns']

		search = None
		# The default search path should always have the
		# hosts default network. If a host has no default
		# network, or if the zone on the default network
		# is empty, leave the search value out.
		for intf in self.call('list.host.interface', [host, 'expanded=True']):
			if intf['default'] is True and intf['zone']:
				search = intf['zone']
				break
		if search:
			self.addOutput(host, f'search {search}')
			
		#
		# If the default network is 'public' use the
		# public DNS rather that the server on the boss.

		#
		# or
		#

		#
		# if any network has 'dns' set to true, then the frontend
		# is serving DNS for that network, so make sure the
		# frontend is listed as the first DNS server, then list
		# the public DNS server. The IP address of the DNS server
		# should be the one on the network that serves out
		# DNS. Not the primary network of the frontend.
		#

		for row in self.call('list.host.interface', [ host ]):
			network = row['network']
			if network in dns and dns[network]:
				frontend = self.getHostAttr(host, 'Kickstart_PrivateAddress')
				for intf in self.call('list.host.interface', ['localhost']):
					if intf['network'] == network:
						frontend = intf['ip']
				self.addOutput(host, 'nameserver %s' % frontend)
				break

		remotedns = self.getHostAttr(host, 'Kickstart_PublicDNSServers')
		if not remotedns:
			remotedns = self.getHostAttr(host, 'Kickstart_PrivateDNSServers')
		if remotedns:
			servers = remotedns.split(',')
			for server in servers:
				self.addOutput(host, 'nameserver %s' % server.strip())


	def run(self, params, args):

		self.beginOutput()

		hosts = self.getHostnames(args)
		for host in hosts:
			osname = self.db.getHostOS(host)
			self.runImplementation(osname, [host])

		self.endOutput(padChar='', trimOwner=True)

