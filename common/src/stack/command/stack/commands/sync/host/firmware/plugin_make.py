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
from stack.exception import CommandError
import stack.firmware

class Plugin(stack.commands.Plugin):
	"""Attempts to sync firmware to hosts"""

	def provides(self):
		return 'make'

	def run(self, args):
		mapped_by_imp_name = {}
		# Remap by implementation name in preparation for running implementations im parallel.
		for host, values_dict in args.items():
			user_specified_imp = values_dict['make_imp']
			# if the user specified a specific implementation to run for this host, use that.
			if user_specified_imp:
				# update if the imp already exists in the map, otherwise add a new key.
				if user_specified_imp in mapped_by_imp_name:
					mapped_by_imp_name[user_specified_imp].update(
						{host: values_dict}
					)
				else:
					mapped_by_imp_name[user_specified_imp] = {host: values_dict}
			# otherwise use the normal name resolution based on attributes
			else:
				imp_name = f"{values_dict['attrs'][stack.firmware.MAKE_ATTR]}"
				# update if the imp already exists in the map, otherwise add a new key.
				if imp_name in mapped_by_imp_name:
					mapped_by_imp_name[imp_name].update(
						{host: values_dict}
					)
				else:
					mapped_by_imp_name[imp_name] = {host: values_dict}

		# we don't expect return values, but the implementations might raise exceptions, so gather them here
		results = self.owner.run_implementations_parallel(
			implementation_mapping = mapped_by_imp_name,
			display_progress = True,
		)
		# drop any results that didn't have any errors and aggregate the rest into one exception
		error_messages = []
		for error in [
			value.exception for value in results.values()
			if value is not None and value.exception is not None
		]:
			# if this looks like a stacki exception type, grab the message from it.
			if hasattr(error, 'message') and callable(getattr(error, 'message')):
				error_messages.append(error.message())
			else:
				error_messages.append(f'{error}')

		if error_messages:
			error_message = '\n'.join(error_messages)
			raise CommandError(
				cmd = self.owner,
				msg = f"Errors occurred during firmware sync:\n{error_message}"
			)
