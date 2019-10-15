# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from concurrent.futures import ThreadPoolExecutor
import stack.commands
from stack.exception import CommandError
from stack.switch.m7800 import SwitchMellanoxM7800

class Implementation(stack.commands.Implementation):

	def list_firmware(self, host, switch_attrs):
		kwargs = {
			'username' : switch_attrs.get('switch_username', None),
			'password' : switch_attrs.get('switch_password', None),
		}

		kwargs = {key: value for key, value in kwargs.items() if value is not None}

		# the context manager ensures we disconnect from the switch
		with SwitchMellanoxM7800(host, **kwargs) as m7800_switch:
			m7800_switch.connect()
			image_listing = m7800_switch.show_images()
			installed_image = image_listing.installed_images[image_listing.last_boot_partition]

		return installed_image

	def run(self, args):
		errors = []
		# now run each image listing in parallel
		with ThreadPoolExecutor(thread_name_prefix = 'mellanox_firmware_listing') as executor:
			futures_by_host_make_model = {
				host_make_model: executor.submit(
					self.list_firmware,
					host = host_make_model.host,
					switch_attrs = attrs
				)
				for host_make_model, attrs in args.items()
			}
			# now collect the results, adding any errors into the errors list
			results_by_host_make_model = {}
			for host_make_model, future in futures_by_host_make_model.items():
				if future.exception() is not None:
					errors.append(future.exception())
				else:
					results_by_host_make_model[host_make_model] = future.result()

		# if there were any errors, aggregate all the errors into one
		error_messages = []
		for error in errors:
			# if this looks like a stacki exception type, grab the message from it.
			if hasattr(error, 'message') and callable(getattr(error, 'message')):
				error_messages.append(error.message())
			else:
				error_messages.append(f'{error}')

		if error_messages:
			error_message = '\n'.join(error_messages)
			raise CommandError(
				cmd = self.owner,
				msg = f"Errors occurred during Mellanox firmware listing:\n{error_message}"
			)

		return results_by_host_make_model
