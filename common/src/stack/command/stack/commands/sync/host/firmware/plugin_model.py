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

from concurrent.futures import ThreadPoolExecutor
import stack.commands

class Plugin(stack.commands.Plugin):
	"""Attempts to sync firmware to hosts"""

	def provides(self):
		return 'model'

	def requires(self):
		return ['make']

	def _run_implementation(self, item):
		make_attr = 'component.make'
		model_attr = 'component.model'
		host, values_dict = item
		self.owner.runImplementation(
			name = f"{values_dict['firmware_attrs'][make_attr]}_{values_dict['firmware_attrs'][model_attr]}",
			args = (host, values_dict['current_firmware_version'], values_dict['file'], values_dict['version'])
		)

	def run(self, args):
		with ThreadPoolExecutor(thread_name_prefix = 'sync_firmware_model_plugin') as executor:
			executor.map(self._run_implementation, args.items())
