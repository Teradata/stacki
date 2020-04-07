# @copyright@
# @copyright@

import stack.commands


class command(stack.commands.NFSRootArgumentProcessor,
	stack.commands.list.command):
	pass


class Command(command):
	"""
	Lists the available nfsroots for the cluster.

	<arg optional='1' type='string' name='image' repeat='1'>
	Optional list of nfsroot names.
	</arg>
	"""

	def run(self, params, args):

		self.beginOutput()
		for nfsroot in self.getNFSRootNames(args):
			rows = self.db.select(
				"""
				o.name, r.tftp, r.nfs
				from nfsroots r, oses o
				where r.name=%s and r.os=o.id
				""", (nfsroot,)
			)
			self.addOutput(nfsroot, rows[0])

		self.endOutput(header=['name', 'os', 'tftp', 'nfs'])
