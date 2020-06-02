# @copyright@
# @copyright@

import os
import shutil
import subprocess
import stack.commands
from stack.argument_processors.os import OSArgProcessor
from stack.exception import CommandError, UsageError, ArgUnique

class command(stack.commands.ImageArgumentProcessor,
	OSArgProcessor,
	stack.commands.add.command):
	pass


class Command(command):
	"""
	Adds an image to the image repository. Images have no namespace
	and no protection from collisions. Images are brand new to stacki,
	and not a mainstream feature yet.

	Images get stored in /export/stack/images and require a name the is
	used within stacki to refer to the file.

	<arg type='string' name='image'>
	Complete pathname to the image being added.
	</arg>

	<param type='string' name='name' optional='0'>
	The name that will be used to refer to this image.
	</param>

	<param type='string' name='os' optional='0'>
	OS associated with the box. Default is the native os (e.g., 'redhat', 'sles').
	</param>

	<param type='string' name='commment'>
	Free form comment (not required).
	</param>
	"""

	def run(self, params, args):
		image_path = '/export/stack/images'

		name, _os, comment = self.fillParams(
			[('name', None, True), 
			 ('os', None, True),
			 ('comment', None)])

		if len(args) != 1:
			raise ArgUnique(self, 'name')
		image = args[0]

		if len(args) != 1:
			raise UsageError(self, 'must supply an image filename')

		if not os.path.exists(image):
			raise CommandError(self, f'{image} does not exists')

		if name in self.getImageNames():
			raise CommandError(self, f'{name} already exists')

		if _os not in self.getOSNames():
			raise ArgNotFound(self, _os, 'OS')

		if not os.path.exists(image_path):
			os.mkdir(image_path)

		shutil.copy(image, os.path.join(image_path, os.path.basename(image)))

		self.db.execute("""
			insert into images(name, os, filename, comment)
			values (%s, (select id from oses where name=%s), %s, %s)
			""", (name, _os, os.path.basename(image), comment))

		
		
		
