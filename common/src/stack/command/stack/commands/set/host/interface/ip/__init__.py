# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import ipaddress
import stack.commands
from stack.exception import ParamRequired, ArgUnique, CommandError


class Command(stack.commands.set.host.command):
	"""
	Sets the IP address for the named interface for one host.

	<arg type='string' name='host' required='1'>
	Host name.
	</arg>
	
	<param type='string' name='interface'>
	Name of the interface.
	</param>

	<param type='string' name='mac'>
	MAC address of the interface.
	</param>

	<param type='string' name='ip' optional='0'>
	IP address
	</param>

	<example cmd='set host interface ip backend-0-0 interface=eth1 ip=192.168.0.10'>
	Sets the IP Address for the eth1 device on host backend-0-0.
	</example>
	"""
	
	def populateIPAddrDict(self, hostname, iface, mac):
		
		# Get network name for this interface
		op = self.call('list.host.interface', [])
		netName = None
		assignedIp = {}

		for o in op:
			interface   = o['interface']
			networkName = o['network']
			macAddr     = o['mac']

			if (interface == iface or macAddr == mac) and \
				hostname == o['host']:
				netName =  o['network']
				#
				# Do not add this host's ip address to the
				# assignIp dictionary
				#
				continue
			
			if networkName not in assignedIp:
				assignedIp[networkName] = [o['ip']]
			else:
				assignedHostIps = assignedIp[networkName]
				assignedHostIps.append(o['ip'])
				assignedIp[networkName] = assignedHostIps

		netAddr = None
		netMask = None

		# Get network address, mask for this network name
		if netName:
			op = self.call('list.network', [ netName ])
			for o in op:
				netAddr = o['address']
				netMask = o['mask']
				break

		# Get list of host addresses for this network
		ipnetwork = ipaddress.IPv4Network(netAddr + '/' + netMask)
		hosts = []

		for h in ipnetwork.hosts():
			hosts.append(str(h))

		# Remove the assigned ip addresses from this list
		for o in assignedIp[netName]:
			if o in hosts:
				hosts.remove(o)
		
		# Return an ip addr from the available addr list
		if len(hosts) > 0:
			return hosts.pop()

		return None

	def run(self, params, args):
		hosts = self.getHostnames(args)
		(ip, interface, mac) = self.fillParams([
			('ip',        None, True),
			('interface', None),
			('mac',       None)
			])

		if not interface and not mac:
			raise ParamRequired(self, ('interface', 'mac'))
		if len(hosts) != 1:
			raise ArgUnique(self, 'host')

		ip   = ip.upper() # null -> NULL
		host = hosts[0]

		if ip == "AUTO":
			ip = self.populateIPAddrDict(host, interface, mac)

			if not ip:
				raise CommandError(self, 'No free ip host addresses left in network')

		if interface:
			self.db.execute("""
				update networks, nodes set 
				networks.ip=NULLIF('%s','NULL') where
				nodes.name='%s' and networks.node=nodes.id and
				networks.device like '%s'
				""" % (ip, host, interface))
		else:
			self.db.execute("""
				update networks, nodes set 
				networks.ip=NULLIF('%s','NULL') where
				nodes.name='%s' and networks.node=nodes.id and
				networks.mac like '%s'
				""" % (ip, host, mac))
