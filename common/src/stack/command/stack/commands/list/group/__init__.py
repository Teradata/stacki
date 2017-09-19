# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.list.command):
	"""
	List the current groups and the number of member hosts in each.
	"""		

	def run(self, params, args):

		self.beginOutput()

		groups = {}

		for row in self.db.select(
			"""
			name from groups
			"""):
			groups[row[0]] = []

		for row in self.db.select(
			"""g.name, n.name
			from groups g, memberships m, nodes n
			where n.id = m.nodeid and g.id = m.groupid
			"""):
			
			groupname, hostname = row
			if groupname in groups:
				groups[groupname].append(hostname)
			else:
				groups[groupname] = hostname

		for group in sorted(groups):
			members = ' '.join(groups[group])
			self.addOutput(group, [members])

		self.endOutput(header=['group', 'hosts'], trimOwner=False)

