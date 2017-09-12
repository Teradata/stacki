# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@


import stack.commands


class Command(stack.commands.list.host.command):
	"""
	Lists the groups for a host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, groups
	for all the known hosts is listed.
	</arg>

	<param type='string' name='group'>
	Restricts the output to only members of a group. This can be a single
	group name or a comma separated list of group names.
	</param>

	<example cmd='list host group backend-0-0'>
	List the groups for backend-0-0.
	</example>
	"""

	def run(self, params, args):

		(group,) = self.fillParams([ ('group', None) ])

		if group:
			groups = group.split(',')
		else:
			groups = None

		self.beginOutput()

		hosts = self.getHostnames(args)
		membership = {}
		
		for host in hosts:
			membership[host] = []
			for row in self.db.select(
				"""
				n.name, g.name from
				groups g, memberships m, nodes n
				where
				n.id = m.nodeid and
				g.id = m.groupid and
				n.name = '%s'
				order by g.name
				""" % host):
				membership[row[0]].append(row[1])
				

		if groups:
			for host in hosts:
				match = []
				for group in membership[host]:
					if group in groups:
						match.append(group)
				if match:
					self.addOutput(host, ' '.join(match))
		else:
			for host in hosts:
				self.addOutput(host, ' '.join(membership[host]))


		self.endOutput(header=['host', 'groups'], trimOwner=False)

