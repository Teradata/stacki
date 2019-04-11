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
import syslog
import stack.commands
from stack.exception import CommandError
from stack.switch.x1052 import SwitchDellX1052
from stack.switch import SwitchException
from stack.expectmore import ExpectMoreException

class Implementation(stack.commands.Implementation):

	def update_firmware(self, switch_name, tftp_ip, software_file_path = None, boot_file_path = None, **kwargs):
		"""Updates the software and/or boot firmware on the provided switch."""
		# No need to continue if we weren't provided any software to upgrade
		if software_file_path is None and boot_file_path is None:
			return

		try:
			x1052_switch = SwitchDellX1052(switch_ip_address = switch_name, switchname = switch_name, **kwargs)
			x1052_switch.set_tftp_ip(ip = tftp_ip)
			x1052_switch.connect()
			# Upload the new software to the switch
			if software_file_path is not None:
				x1052_switch.upload_software(software_file = software_file_path)

			# Upload the new boot firmware to the switch
			if boot_file_path is not None:
				x1052_switch.upload_boot(boot_file = boot_file_path)

			# Reboot the switch to apply the updates
			x1052_switch.reload()
		# Turn some potentially verbose and detailed error messages into something more end user friendly
		# while keeping the dirty details available in the logs.
		except (SwitchException, ExpectMoreException) as exception:
			stack.commands.Log(
				message = f"Error during firmware update on {switch_name}: {exception}",
				level = syslog.LOG_ERR
			)
			raise CommandError(
				cmd = self.owner,
				msg = f"Failed to update firmware on {switch_name}."
			)

	def run(self, args):
		"""Runs the firmware update for each provided Dell x1052 switch in parallel."""
		# Since we can update both the boot and the software version based on the hostname, collapse the
		# "software" and the "boot" models together into one.
		software_key = "software_file_path"
		boot_key = "boot_file_path"
		x1052_firmware_args_per_host = {
			switch_name_make_model.host: {software_key: None, boot_key: None}
			for switch_name_make_model in args
		}
		for switch_name_make_model, firmware_info in args.items():
			# There is no currently known valid multi-file use case for Dell for a given model grouping (x1052-software and/or x1052-boot).
			# We don't care if the user tried to force multiple firmware files down our throats.
			if len(firmware_info.firmware_files) > 1:
				raise CommandError(
					self.owner,
					msg = (
						"Firmware update for Dell switches cannot operate on multiple firmware files at once."
						" Please fix your configuration and try again."
					)
				)

			# Generate a set of switch kwargs
			kwargs = {
				"username": firmware_info.host_attrs.get("switch_username"),
				"password": firmware_info.host_attrs.get("switch_password"),
			}
			kwargs = {key: value for key, value in kwargs.items() if value is not None}

			# Update the software or boot dictionary key based on the model for this firmware file.
			firmware_file = firmware_info.firmware_files.pop()
			if "boot" in switch_name_make_model.model:
				update_key = boot_key
			else:
				update_key = software_key

			x1052_firmware_args_per_host[switch_name_make_model.host].update(
				{update_key: firmware_file.file, "tftp_ip": firmware_info.frontend_ip, **kwargs}
			)

		errors = []
		# now run each switch upgrade in parallel
		with ThreadPoolExecutor(thread_name_prefix = "dell_firmware_update") as executor:
			futures = [
				executor.submit(self.update_firmware, switch_name = switch_name, **switch_args)
				for switch_name, switch_args in x1052_firmware_args_per_host.items()
			]
			# Collect any errors, we don't expect there to be any return values.
			for future in futures:
				errors.append(future.exception())

		# drop any Nones returned because of no exceptions and aggregate all remaining errors into one
		error_messages = []
		for error in [error for error in errors if error is not None]:
			# if this looks like a stacki exception type, grab the message from it.
			if hasattr(error, 'message') and callable(getattr(error, 'message')):
				error_messages.append(error.message())
			else:
				error_messages.append(f'{error}')

		if error_messages:
			error_message = '\n'.join(error_messages)
			raise CommandError(
				cmd = self.owner,
				msg = f"Errors occurred during Dell firmware upgrade:\n{error_message}"
			)
