# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@

import stack.commands
from stack.commands import ApplianceArgProcessor
from stack.exception import CommandError


class Plugin(ApplianceArgProcessor, stack.commands.Plugin):

	def provides(self):
		return 'default'

	def run(self, args):
		appliances = self.getApplianceNames()

		for target, data in args.items():
			# Remove all existing entries
			cmdargs = []

			if target != 'global':
				cmdargs.append(target)

			cmdargs += ['adapter=*', 'enclosure=*', 'slot=*']

			try:
				if target == 'global':
					self.owner.call('remove.storage.controller', cmdargs)
				elif target in appliances:
					self.owner.call('remove.appliance.storage.controller', cmdargs)
				else:
					self.owner.call('remove.host.storage.controller', cmdargs)
			except CommandError:
				# Nothing existed to remove
				pass

			# Add the new ones
			# arrayid can be int, 'global', or '*'
			# this key function works by offering a tuple of (is_string, value) for sorting
			# this will sort by bool first, falling back to value if the bools are equal
			# this puts non-strings first (False<True), then ascending order
			for array in sorted(data, key=lambda i: (isinstance(i, str), i)):
				cmdargs = []
				if target != 'global':
					cmdargs.append(target)

				cmdargs += [f'arrayid={array}']

				if 'raid' in data[array]:
					raidlevel = data[array]['raid']
					cmdargs.append(f'raidlevel={raidlevel}')

				if 'slot' in data[array]:
					slots = ','.join(str(s) for s in data[array]['slot'])

					if slots:
						cmdargs.append(f'slot={slots}')

				if 'enclosure' in data[array]:
					enclosure = data[array]['enclosure'].strip()
					cmdargs.append(f'enclosure={enclosure}')

				if 'adapter' in data[array]:
					adapter = data[array]['adapter'].strip()
					cmdargs.append(f'adapter={adapter}')

				if 'options' in data[array]:
					options = data[array]['options']
					cmdargs.append(f'options="{options}"')

				if 'hotspare' in data[array]:
					hotspares = ','.join(str(h) for h in data[array]['hotspare'])

					if hotspares:
						cmdargs.append(f'hotspare={hotspares}')

				if target == 'global':
					self.owner.call('add.storage.controller', cmdargs)
				elif target in appliances:
					self.owner.call('add.appliance.storage.controller', cmdargs)
				else:
					self.owner.call('add.host.storage.controller', cmdargs)
