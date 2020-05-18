# @copyright@
# @copyright@

import stack.commands

class Command(stack.commands.set.host.command,
	      stack.commands.NFSRootArgumentProcessor):
	"""
	Sets the nfsroot for a list of hosts.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='nfsroot' optional='0'>
	The name of the nfsroot
	</param>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		nfsroot, = self.fillParams([
			('nfsroot', None, True)
		])

		if nfsroot: # check to make sure this is a valid nfsroot name
			self.getNFSRootNames([ nfsroot ])

		for host in hosts:
			self.db.execute("""
				update nodes set nfsroot=(
					select id from nfsroots where name=%s
				) where name=%s
			""", (nfsroot, host))
