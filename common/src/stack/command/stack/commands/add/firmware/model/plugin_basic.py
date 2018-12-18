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
		models = set(args)
		# ensure the model name doesn't already exist for the given make
		existing_makes_models = [
			(make, model)
			for make, model, count in (
				(
					make,
					model,
					self.owner.db.count(
						'''
						(firmware_model.id)
						FROM firmware_model
							INNER JOIN firmware_make
								ON firmware_model.make_id=firmware_make.id
						WHERE firmware_model.name=%s AND firmware_make.name=%s
						''',
						(model, make)
					)
				)
				for model in models
			)
			if count > 0
		]
		if existing_makes_models:
			raise CommandError(cmd = self.owner, msg = f'The following make and model combinations already exist {existing_makes_models}.')

		# create the make if it doesn't already exist
		if not self.owner.db.count('(id) FROM firmware_make WHERE name=%s', make):
			self.owner.call(command = 'add.firmware.make', args = [make])

		# get the ID of the make to associate with
		make_id = self.owner.db.select('id FROM firmware_make WHERE name=%s', make)[0][0]

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
