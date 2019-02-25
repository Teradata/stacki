# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
from copy import copy
import stack.commands
from stack.exception import CommandError, ArgRequired


class Command(stack.commands.set.pallet.command):
	"""
	Sets a tag for one or more pallets.

	<arg type='string' name='pallet' repeat='1'>
	Name of one or more pallets.
	</arg>

	<param type='string' name='tag' optional='0'>
	Name of the tag
	</param>

	<param type='string' name='value' optional='0'>
	Value of the attribute
	</param>

	<param type='string' name='version'>
	Version of the pallet
	</param>

	<param type='string' name='release'>
	Release of the pallet
	</param>

	<param type='string' name='arch'>
	Arch of the pallet
	</param>

	<param type='string' name='os'>
	OS of the pallet
	</param>
	"""

	def run(self, params, args):

		if len(args) < 1:
			raise ArgRequired(self, 'pallet')

		(tag, value, force) = self.fillParams([
			('tag',    None, True),
			('value',  None, True),
			('force',  True),
			])

		force = self.str2bool(force)

		if value and not re.match('^[a-zA-Z_][a-zA-Z0-9_.]*$', tag):
			raise CommandError(self, f'invalid tag name "{tag}"')

		
		pallets = self.getPallets(args, params)

		# If the tag is already defined and force=False
		# complain
		#
		# 	add := force=false
		# 	set := force=true
		if not force:
			for p in pallets:
				name = f'{p.name}-{p.version}-{p.rel}-{p.arch}-{p.os}'
				for row in self.call('list.pallet.tag', [
					p.name,
					f'version={p.version}',
					f'release={p.rel}',
					f'arch={p.arch}',
					f'os={p.os}',
					f'tag={tag}'
					]):
					raise CommandError(self, 
							   f'tag "{tag}" exists for {name}')
	

		for p in pallets:
			# To avoid 'update' vs 'insert' nonsense just remove
			# the tag first (not an error if it doesn't exist)
			self.db.execute("""
				delete from tags where
				scope   = 'pallet' and 
				scopeid = %s and
				tag     = %s
				""", (p.id, tag))

			if not value:
				# Passing `value=` to command will delete
				continue

			self.db.execute("""
				insert into tags
				(scope, tag, value, scopeid)
				values ('pallet', %s, %s, %s)
				""", (tag, value, p.id))
