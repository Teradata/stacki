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

class Plugin(stack.commands.Plugin):
	"""Attempts to add all provided model names to the database associated with the given make."""

	def provides(self):
		return 'basic'

	def run(self, args):
		params, args = args
		# Require at least one model name
		if not args:
			raise ArgRequired(cmd = self.owner, arg = 'model')

		make, = self.owner.fillParams(
			names = [('make', None)],
			params = params
		)

		# require a make
		if make is None:
			raise ParamRequired(cmd = self.owner, param = 'make')

		# get rid of any duplicate names
		models = self.owner.remove_duplicates(args = args)
		# ensure the model name doesn't already exist for the given make
		self.owner.validate_unique_models(make = make, models = models)

		# create the make if it doesn't already exist
		if not self.owner.make_exists(make = make):
			self.owner.call(command = 'add.firmware.make', args = [make])

		# get the ID of the make to associate with
		make_id = self.owner.get_make_id(make = make)

		for model in models:
			self.owner.db.execute(
				'''
				INSERT INTO firmware_model (
					name,
					make_id
				)
				VALUES (%s, %s)
				''',
				(model, make_id)
			)
