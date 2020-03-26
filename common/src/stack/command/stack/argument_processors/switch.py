# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

from stack.cond import EvalCondExpr
from stack.exception import CommandError, ArgNotFound
from stack.util import flatten

class SwitchArgProcessor:
	"""
	An interface class to add the ability to process switch arguments.
	"""

	def getSwitchNames(self, args=None):
		"""
		Returns a list of switch names from the database. For each arg
		in the ARGS list find all the switch names that match the arg
		(assume SQL regexp). If an arg does not match anything in the
		database we raise an exception. If the ARGS list is empty return
		all network names.
		"""

		switches = []
		if not args:
			args = ['%'] # find all switches

		for arg in args:
			names = flatten(self.db.select("""
				n.name from nodes n, appliances a
				where n.appliance=a.id and a.name='switch' and n.name like %s
				order by rack, rank
			""", (arg,)))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'switch')

			switches.extend(names)

		return switches

	def delSwitchEntries(self, args=None):
		"""
		Delete foreign key references from switchports
		"""

		if not args:
			return

		for arg in args:
			self.db.execute("""
				delete from switchports
				where switch=(select id from nodes where name=%s)
			""", (arg,))

	def getSwitchNetwork(self, switch):
		"""
		Returns the network the switch's management interface is on.
		"""

		if not switch:
			return ''

		rows = self.db.select("""
			subnet from networks
			where node=(select id from nodes where name=%s)
		""", (switch,))

		if rows:
			network = rows[0][0]
		else:
			network = ''

		return network

	def doSwitchHost(self, switch, port, host, interface, action):
		rows = self.db.select("""
			id from networks
			where node=(select id from nodes where name=%s) and device=%s
		""", (host, interface))

		try:
			host_interface = rows[0][0]
		except:
			host_interface = None

		if not host_interface:
			raise CommandError(self,
				"Interface '%s' isn't defined for host '%s'"
				% (interface, switch))

		# Check if the port is already managed by the switch
		rows = self.db.select("""
			* from switchports
			where interface=%s and port=%s
			and switch=(select id from nodes where name=%s)
		""", (host_interface, port, switch))

		if action == 'remove' and rows:
			# delete it
			self.db.execute("""
				delete from switchports
				where interface=%s and switch=(
					select id from nodes where name=%s
				) and port=%s
			""", (host_interface, switch, port))
		elif action == 'add' and not rows:
			# add it
			self.db.execute("""
				insert into switchports (interface, switch, port)
				values (%s, (select id from nodes where name=%s), %s)
			""", (host_interface, switch, port))

	def addSwitchHost(self, switch, port, host, interface):
		"""
		Add a host/interface to a switch/port
		"""
		self.doSwitchHost(switch, port, host, interface, 'add')

	def delSwitchHost(self, switch, port, host, interface):
		"""
		Remove a host/interface from a switch/port
		"""
		self.doSwitchHost(switch, port, host, interface, 'remove')

	def getHostsForSwitch(self, switch):
		"""
		Return a dictionary of hosts that are connected to the switch.
		Each entry will be keyed off of the port since most of the information
		stored by the switch is based off port.
		"""

		hosts = {}
		rows = self.db.select("""
			n.name, i.device, s.port, i.vlanid, i.mac
			from nodes n, networks i, switchports s
			where s.switch=(select id from nodes where name=%s)
			and i.id=s.interface and n.id=i.node
		""", (switch,))

		for host, interface, port, vlanid, mac in rows:
			hosts[str(port)] = {
				'host': host,
				'interface': interface,
				'port': port,
				'vlan': vlanid,
				'mac': mac,
			}

		return hosts
