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


import stack.commands
from stack.exception import CommandError


class Command(stack.commands.swap.host.command):
	"""
	Swaps two host interfaces in the database.

	<arg type='string' name='host' optional='1'>
	Host name of machine
	</arg>

	<param type='string' name='interfaces' optional='0'>
	Two comma-separated interface names (e.g., interfaces="eth0,eth1").
	</param>

	<param type='boolean' name='sync-config'>
	If "yes", then run 'rocks sync config' at the end of the command.
	The default is: yes.
	</param>
	"""

	def swap(self, host, old_mac, old_interface, new_mac, new_interface):
		#
		# swap two interfaces
		#
		rows = self.db.execute("""select id,module,options from
			networks where mac = '%s' and node = (select id from
			nodes where name = '%s') """ % (old_mac, host))
		if rows != 1:
			return

		(old_id, old_module, old_options) = self.db.fetchone()

		rows = self.db.execute("""select id,module,options from
			networks where mac = '%s' and node = (select id from
			nodes where name = '%s') """ % (new_mac, host))
		if rows != 1:
			return

		(new_id, new_module, new_options) = self.db.fetchone()

		self.db.execute("""update networks set mac = '%s',
			device = '%s' where id = %s""" % (old_mac, old_interface,
			new_id))

		self.db.execute("""update networks set mac = '%s',
			device = '%s' where id = %s""" % (new_mac, new_interface,
			old_id))

		if old_module:
			self.db.execute("""update networks set module = '%s'
				where id = %s""" % (old_module, new_id))
		if new_module:
			self.db.execute("""update networks set module = '%s'
				where id = %s""" % (new_module, old_id))
		if old_options:
			self.db.execute("""update networks set options = '%s'
				where id = %s""" % (old_options, new_id))
		if new_options:
			self.db.execute("""update networks set options = '%s'
				where id = %s""" % (new_options, old_id))


	def run(self, params, args):
		interfaces, sync_config = self.fillParams([
			('interfaces', None, True),
			('sync-config', 'yes')
			])

		syncit = self.str2bool(sync_config)

		interface = interfaces.split(',')
		if len(interface) != 2:
			raise CommandError(self, 'must supply two interfaces')

		hosts = self.getHostnames(args)
		for host in hosts:
			mac = []

			self.db.execute("""
				select mac from networks where node =
				(select id from nodes where name = '%s') and
				device = '%s' """ % (host, interface[0]))

			m, = self.db.fetchone()
			mac.append(m)

			self.db.execute("""select mac from networks where node =
				(select id from nodes where name = '%s') and
				device = '%s' """ % (host, interface[1]))

			m, = self.db.fetchone()
			mac.append(m)

			self.swap(host, mac[0], interface[0], mac[1], interface[1])

		if syncit:
			self.command('sync.host.config', hosts)	
			self.command('sync.host.network', hosts)	

