# @copyright@
# @copyright@

import stack.commands


class command(stack.commands.ImageArgumentProcessor,
	stack.commands.list.command):
	pass


class Command(command):
	"""
	Lists the available images for the cluster.

	<arg optional='1' type='string' name='image' repeat='1'>
	Optional list of image names.
	</arg>

	<example cmd='list image'>
	List all known images.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()
		for image in self.getImageNames(args):
			rows = self.db.select(
				"""
				o.name, i.filename, i.comment
				from images i, oses o
				where i.name=%s and i.os=o.id
				""", (image,)
			)
			self.addOutput(image, rows[0])

		self.endOutput(header=['name', 'os', 'image', 'comment'])
