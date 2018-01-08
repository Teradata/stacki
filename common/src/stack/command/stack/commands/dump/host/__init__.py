# @copyright@
# Copyright (c) 2006 - 2017 Teradata
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


class command(stack.commands.HostArgumentProcessor,
	stack.commands.dump.command):

	def dumpHostname(self, hostname):
		if hostname == self.db.getHostname():
			return 'localhost'
		else:
			return hostname

	
class Command(command):
	"""
	Dump the host information as rocks commands.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, 
	information for all hosts will be listed.
	</arg>

	<example cmd='dump host backend-0-0'>
	Dump host backend-0-0 information.
	</example>
	
	<example cmd='dump host backend-0-0 backend-0-1'>
	Dump host backend-0-0 and backend-0-1 information.
	</example>
		
	<example cmd='dump host'>
	Dump all hosts.
	</example>
	"""

	def run(self, params, args):
		for host in self.getHostnames(args):
			self.db.execute("""select 
				n.rack, n.rank, a.longname, 
				n.osaction, n.installaction
				from nodes n, appliances a where
				n.appliance=a.id and n.name='%s'""" % host)
			(rack, rank, longname, osaction,
				installaction) = self.db.fetchone()

			# do not dump the localhost since the installer
			# will add the host for us

			if self.db.getHostname() == host:
				continue

			self.dump('"add host" %s rack=%s rank=%s '
				'longname=%s' %
				(host, rack, rank, 
				self.quote(longname)))

			#
			# now set the osaction and installaction for each host
			#
			if osaction:
				self.dump('"set host osaction" %s action=%s'
					% (host, self.quote(osaction)))
			if installaction:
				self.dump('"set host installaction" %s action=%s'
					% (host, self.quote(installaction)))


