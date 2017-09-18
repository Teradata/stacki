# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class command(stack.commands.HostArgumentProcessor, stack.commands.set.command):

	def verifyInterface(self, host, interface):
		"""
		Returns True IFF the host has the specificied interface.
		"""
		exists = False
		for row in self.db.select("""
			* from
			networks net, nodes n where
			n.name = '%s' and net.device = '%s' and
			n.id = net.node
			""" % (host, interface)):
			exists = True

		return exists
			
	def getInterface(self, host, network):
		"""
		Returns the interface name of a host for the specified network.
		"""
		interface = None
		for interface, in self.db.select("""
			net.device from
			networks net, subnets s, nodes n where
			n.name='%s' and s.name='%s' and
			n.id = net.node and
			s.id = net.subnet
			""" % (host, network)):
			pass

		return interface
			

