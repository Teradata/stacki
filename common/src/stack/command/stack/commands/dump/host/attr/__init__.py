# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@


import stack.attr
import stack.commands


class Command(stack.commands.dump.host.command):
	"""
	Dump the set of attributes for hosts.

	<arg optional='1' type='string' name='host'>
	Host name of machine
	</arg>
	
	<example cmd='dump host attr compute-0-0'>
	Dump the attributes for compute-0-0.
	</example>
	"""

	def run(self, params, args):

		hosts = self.getHostnames(args)

		try:
			self.db.execute("""
				select n.name, a.scope, a.attr,
				a.value, a.shadow from 
				node_attributes a, nodes n where
				a.node=n.id
				order by n.name, a.scope, a.value
				""")
		except:
			self.db.execute("""
				select n.name, a.scope, a.attr,
				a.value from 
				node_attributes a, nodes n where
				a.node=n.id
				order by n.name, a.scope, a.value
				""")
			
		for row in self.db.fetchall():

			host   = row[0]
			attr   = stack.attr.ConcatAttr(row[1], row[2])
			value  = self.quote(row[3])
			shadow = ''
			if len(row) == 5 and row[4]:
				value  = self.quote(row[4])
				shadow = 'shadow=true'
				
			# Filter out rows for hosts we don't care about.
			# Easier to do this post than use multiple
			# select statements.
			
			if host not in hosts:
				continue

			# Don't dump the os and arch attributes since
			# they are set by kickstart.  This allows
			# nodes to change their os/arch after a
			# restore roll is applied to a upgraded
			# cluster.
			#
			# Are there more attributes we need add to this
			# exclude list?

			if attr in [ 'arch', 'os' ]:
				continue

			if value:
				self.dump('add host attr %s attr=%s value=%s %s' %
					  (host, attr, value, shadow))

