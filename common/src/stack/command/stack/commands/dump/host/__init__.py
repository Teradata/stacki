# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
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

	<example cmd='dump host compute-0-0'>
	Dump host compute-0-0 information.
	</example>
	
	<example cmd='dump host compute-0-0 compute-0-1'>
	Dump host compute-0-0 and compute-0-1 information.
	</example>
		
	<example cmd='dump host'>
	Dump all hosts.
	</example>
	"""

	def run(self, params, args):
		for host in self.getHostnames(args):
			self.db.execute("""select 
				n.rack, n.rank, a.longname, 
				n.runaction, n.installaction
				from nodes n, appliances a where
				n.appliance=a.id and n.name='%s'""" % host)
			(rack, rank, longname, runaction,
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
			# now set the runaction and installaction for each host
			#
			if runaction:
				self.dump('"set host runaction" %s action=%s'
					% (host, self.quote(runaction)))
			if installaction:
				self.dump('"set host installaction" %s action=%s'
					% (host, self.quote(installaction)))


