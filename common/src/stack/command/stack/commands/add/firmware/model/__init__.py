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
from stack.exception import ArgRequired, CommandError, ParamRequired


class Command(stack.commands.add.firmware.command):
	"""
	Adds a firmware model to the stacki database.

	<arg type='string' name='model' repeat='1'>
	One or more model names to add. model names are required to be unique, and any duplicates will be ignored.
	</arg>

	<param type='string' name='make'>
	The maker of the models being added. If this does not correspond to an already existing make, one will be added.
	</param>

	<example cmd="add firmware model awesome_9001 mediocre_5200 make='boss hardware corp'">
	Adds two models with the names 'awesome_9001' and 'mediocre_5200' to the set of available firmware models under the 'boss hardware corp' make.
	</example>
	"""

	def run(self, params, args):
		# Require at least one model name
		if not args:
			raise ArgRequired(self, 'model')

		make, = self.fillParams(
			names = [('make', None)],
			params = params
		)

		# require a make
		if make is None:
			raise ParamRequired(cmd = self, param = 'make')

		# get rid of any duplicate names
		models = set(args)
		# ensure the model name doesn't already exist for the given make
		for model in models:
			if self.db.count(
				'''
				(firmware_model.id), firmware_model.make_id, firmware_make.id
				FROM firmware_model
					INNER JOIN firmware_make
						ON firmware_model.make_id=firmware_make.id
				WHERE firmware_model.name=%s AND firmware_make.name=%s
				''',
				(model, make)
			) > 0:
				raise CommandError(cmd = self, msg = f'Firmware model with name {model} already exists for make {make}.')

		# create the make if it doesn't already exist
		if not self.db.count('(id) FROM firmware_make WHERE name=%s', make):
			self.call(command = 'add.firmware.make', args = [make])

		# get the ID of the make to associate with
		make_id = self.db.select('(id) FROM firmware_make WHERE name=%s', make)[0][0]
		# pass the models and the make_id t the plugins
		self.runPlugins(args = (models, make_id))
