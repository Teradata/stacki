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

import stack.commands
import subprocess
from stack.exception import CommandError


class Command(stack.commands.add.host.command):
	"""
	Add a route for a host

	<arg type='string' name='host' repeat='1'>
	Host name of machine
	</arg>
	
	<param type='string' name='address'>
	Host or network address
	</param>
	
	<param type='string' name='gateway'>
	Network or device gateway
	</param>

	<param type='string' name='interface'>
	The interface to send the bits over. Useful if 
	you want to tag a packet.
	</param>

	<param type='string' name='syncnow'>
	Add route to the routing table immediately
	</param>

	<param type='string' name='netmask'>
	Specifies the netmask for a network route.  For a host route
	this is not required and assumed to be 255.255.255.255
	</param>

	<example cmd="add host route localhost address=10.0.0.2 gateway=10.0.0.1 interface=eth1.2 syncnow=true">
	Add a host based route on the frontend to address 10.0.0.2 with the gateway 10.0.0.1
	through interface eth1.2. This will tag the packet with the vlan ID of 2.
	The syncnow flag being set to true will also add it to the live routing table so no network restart
	is needed.
	</example>
	"""

	def run(self, params, args):

		hosts = self.getHostnames(args)
		
		(address, gateway, netmask, interface, syncnow) = self.fillParams([
			('address', None, True),
			('gateway', None, True),
			('netmask', '255.255.255.255'),
			('interface', None),
			('syncnow', None),
			])
		
		syncnow = self.str2bool(syncnow)

		#
		# determine if this is a subnet identifier
		#
		subnet = 0
		rows = self.db.execute("""select id from subnets where
			name = '%s' """ % gateway)

		if rows == 1:
			subnet, = self.db.fetchone()
			gateway = ""
		else:
			subnet = 'NULL'
			gateway = "%s" % gateway
		
		# Verify the route doesn't already exist.  If it does
		# for any of the hosts raise a CommandError.
		
		for host in hosts:
			_rows = self.db.select("""
				r.network, r.interface, r.gateway from
				node_routes r, nodes n where
				r.node=n.id and
				r.network='%s' and
				n.name='%s'
				""" % (address, host))
			if _rows:
				if host != self.db.getHostname('localhost'):
					raise CommandError(self, 'route exists')

				if syncnow and host == self.db.getHostname('localhost'):
					if self.os == 'sles':
						for _row in _rows:
							_ip = _row[0]
							_device = _row[1].split(':')[0]
							_gateway = _row[2]
							_args = [
								'localhost',
								'address=%s' % _ip,
								'interface=%s' % _device,
								'gateway=%s' % _gateway,
								'syncnow=true',
								]

							self.call('remove.host.route', _args)

		#
		# if interface is being set, check if it exists first
		#
		if interface:
			rows = self.db.execute("""select * from networks
				where node=1 and device='%s'""" % interface)
			if not rows:
				raise CommandError(self, 'interface does not exist')
		else:
			interface='NULL'
		
		# Now that we know things will work insert the route for
		# all the hosts
		
		for host in hosts:	
			self.db.execute("""insert into node_routes values 
				((select id from nodes where name='%s'),
				'%s', '%s', '%s', %s, '%s')""" %
				(host, address, netmask, gateway, subnet, interface))
			
			#
			# if host is frontend and sync now, add route to routing table
			#
			if host in self.getHostnames(['localhost']):
				if syncnow:
					add_route = ['route', 'add', '-host', address]

					if interface and interface != 'NULL':
						add_route.append('dev')
						add_route.append(interface)

					if gateway:
						add_route.append('gw')
						add_route.append(gateway)

					# add route to routing table
					p = subprocess.Popen(add_route, stdout=subprocess.PIPE)
					
					# add route to routes file
					cmd = '/opt/stack/bin/stack report host route localhost | '
					cmd += '/opt/stack/bin/stack report script | '
					cmd += 'bash > /dev/null 2>&1 '

					p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
