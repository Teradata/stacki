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


class Command(stack.commands.list.host.command):
	"""
	Lists the current bot action for hosts. For each host supplied on the
	command line, this command prints the hostname and boot action for
	that host. The boot action describes what the host will do the next
	time it is booted.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host boot backend-0-0'>
	List the current boot action for backend-0-0.
	</example>

	<example cmd='list host boot'>
	List the current boot action for all known hosts.
	</example>
	"""

	def run(self, params, args):

		boot = {}
		for h, b in self.db.select(
			"""
			n.name, b.action from nodes n
			left join boot b on
			n.id = b.node
			"""):
			boot[h] = b

		self.beginOutput()
		for host in self.getHostnames(args):
			nukecontroller = False
			nukedisks = self.getHostAttr(host, 'nukedisks')
			if not nukedisks:
				nukedisks = False
			else:
				nukedisks = self.str2bool(nukedisks)
			nukecontroller = self.getHostAttr(host, 'nukecontroller')
			if not nukecontroller:
				nukecontroller = False
			else:
				nukecontroller = self.str2bool(nukecontroller)
			self.addOutput(host, (boot[host], nukedisks, nukecontroller))

		self.endOutput(header=['host', 'action', 'nukedisks', 'nukecontroller'])


RollName = "stacki"
