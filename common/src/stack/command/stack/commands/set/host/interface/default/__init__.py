# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ParamRequired, CommandError


class Command(stack.commands.set.host.interface.command):
	"""
	Designates one network as the default route for a set of hosts.
	Either the interface or network paramater is required.

	<arg optional='1' repeat='1' type='string' name='host'>
	Host name.
	</arg>
	
	<param optional='0' type='string' name='interface'>
	Device name of the default interface.
	</param>

	<param optional='0' type='string' name='network'>
	Network name of the default interface.
	</param>

	<param optional='0' type='string' name='mac'>
	MAC address name of the default interface.
	</param>

	<param optional='0' type='bool' name='default'>
	Can be used to set the value of default to False.
	</param>
	"""

	def run(self, params, args):

		(default, interface, network, mac) = self.fillParams([
			('default', 'true'),
			('interface', None),
			('network', None),
			('mac', None),
			])

		default = self.str2bool(default)

		if not interface and not network and not mac:
			raise ParamRequired(self, ('interface', 'network', 'mac'))

		for host in self.getHostnames(args):
			valid = False
			# Check validity of params. Match them against the
			# values in the database to check params.
			for dict in self.call('list.host.interface', [host]):
				if network and network == dict['network']:
					valid = True
					sql_set_cmd = """update networks net,
					nodes n, subnets s set net.main = %d
					where n.name = '%s' and s.name='%s'
					and net.node = n.id and net.subnet=s.id""" % \
					(default, host, network)
					break
				if interface and interface == dict['interface']:
					valid = True
					sql_set_cmd = """update networks net,
					nodes n set net.main = %d where
					n.name = '%s' and net.node = n.id
					and net.device ='%s'""" % \
					(default, host, interface)
					break
				if mac and mac == dict['mac']:
					valid = True
					sql_set_cmd = """update networks net,
					nodes n set net.main = %d where
					n.name = '%s' and net.node = n.id
					and net.mac ='%s'""" % \
					(default, host, mac)
					break
			if valid:
				if default:
					sql_clear_cmd = """update networks net,
						nodes n set net.main = 0
						where n.name = '%s' and
						net.node = n.id """ % (host)
					self.db.execute(sql_clear_cmd)
				self.db.execute(sql_set_cmd)
			else:
				if network:
					raise CommandError(self, "Network '%s' for '%s' not found" % 
						(network, host))
				elif interface:
					raise CommandError(self, "Interface '%s' for '%s' not found" % 
						(interface, host))
				elif mac:
					raise CommandError(self, "MAC Address '%s' for '%s' not found" % 
						(mac, host))
