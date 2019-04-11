# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from concurrent.futures import ThreadPoolExecutor
import stack.commands
from stack.exception import CommandError
from stack.switch.x1052 import SwitchDellX1052

class Implementation(stack.commands.Implementation):

	def list_firmware(self, host, switch_attrs):
		kwargs = {
			"username" : switch_attrs.get("switch_username"),
			"password" : switch_attrs.get("switch_password"),
		}

		kwargs = {key: value for key, value in kwargs.items() if value is not None}

		# the context manager ensures we disconnect from the switch
		with SwitchDellX1052(switch_ip_address = host, switchname = host, **kwargs) as x1052_switch:
			x1052_switch.connect()
			return x1052_switch.get_versions()

	def run(self, args):
		errors = []
		# Since we can get both the boot and the software version based on the hostname, collapse the
		# "software" and the "boot" models together into one.
		x1052_attrs_per_host = {
			host_make_model.host: {} for host_make_model in args
		}
		for host_make_model, attrs in args.items():
			x1052_attrs_per_host[host_make_model.host].update(attrs)

		# now run each image listing in parallel
		with ThreadPoolExecutor(thread_name_prefix = "dell_firmware_listing") as executor:
			futures_by_host = {
				host: executor.submit(
					self.list_firmware,
					host = host,
					switch_attrs = attrs
				)
				for host, attrs in x1052_attrs_per_host.items()
			}
			# now collect the results, adding any errors into the errors list
			results_by_host = {}
			for host, future in futures_by_host.items():
				if future.exception() is not None:
					errors.append(future.exception())
				else:
					results_by_host[host] = future.result()

		# if there were any errors, aggregate all the errors into one
		error_messages = []
		for error in errors:
			# if this looks like a stacki exception type, grab the message from it.
			if hasattr(error, "message") and callable(getattr(error, "message")):
				error_messages.append(error.message())
			else:
				error_messages.append(f'{error}')

		if error_messages:
			error_message = '\n'.join(error_messages)
			raise CommandError(
				cmd = self.owner,
				msg = f"Errors occurred during Dell firmware listing:\n{error_message}"
			)

		# Split results back out into host_make_model.
		return {
			host_make_model: results_by_host[host_make_model.host].boot if "boot" in host_make_model.model else results_by_host[host_make_model.host].software
			for host_make_model in args
		}
