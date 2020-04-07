# @copyright@
# @copyright@

import stack.commands

class Command(stack.commands.set.host.command,
	      stack.commands.ImageArgumentProcessor):
	"""
	Sets the image for a list of hosts.

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='image' optional='0'>
	The name of the image (e.g. default)
	</param>
	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		image, = self.fillParams([
			('image', None, True)
		])

		if image: # check to make sure this is a valid image name
			self.getImageNames([ image ])

		for host in hosts:
			self.db.execute("""
				update nodes set image=(
					select id from images where name=%s
				) where name=%s
			""", (image, host))
