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


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'cleanup'

	def requires(self):
		return [ 'HEAD' ]
		
	def removerow(self, interfaceid):
		self.owner.db.execute("""delete from networks where id = '%s'""" % interfaceid)

	def ifclean(self, interfaceid, interface):
		#
		# - turn off the interface
		# - remove the ifcfg file (if necessary)
		# - remove it from the live configuration
		#
		import subprocess
		import os

		if ':' in interface:
			physif = interface.split(':')[0]
		else:
			physif = interface

		subprocess.call([ 'ifdown', physif ], stdout=open('/dev/null'),
			stderr=open('/dev/null'))

		ifcfg = '/etc/sysconfig/network/ifcfg-%s' % physif
		if os.path.exists(ifcfg):
			os.remove(ifcfg)
			
		self.removerow(interfaceid)

		#
		# since we are removing interfaces from the frontend, there are instances in
		# which the interface that contains the name of the frontend is removed, therefore
		# 'getHostname("localhost")' lookup will fail because there is no name in the
		# database.
		#
		try:
			localhost = self.owner.db.getHostname('localhost')
		except:
			localhost = None

		if localhost:
			self.owner.call('sync.host.network', [ 'localhost', 'restart=n' ])

			if os.path.exists(ifcfg):
				subprocess.call([ 'ifup', physif ], stdout=open('/dev/null'),
					stderr=open('/dev/null'))

	def run(self, networks):
		for interfaceid in networks:
			self.owner.db.execute("""select n.name, net.device
				from networks net, nodes n
				where net.id = '%s' and n.id = net.node""" % interfaceid)

			host, interface = self.owner.db.fetchone()

			try:
				host = self.owner.db.getHostname(host)
			except:
				host = None

			try:
				localhost = self.owner.db.getHostname('localhost')
			except:
				localhost = None

			if host and localhost and host == localhost:
				#
				# if this is the frontend, so some local cleanup
				#
				self.ifclean(interfaceid, interface)
			else:
				self.removerow(interfaceid)

