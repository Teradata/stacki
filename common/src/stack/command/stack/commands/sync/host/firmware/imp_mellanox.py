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

from threading import Timer
from contextlib import suppress
from concurrent.futures import ThreadPoolExecutor
import syslog
import stack.commands
from stack.exception import CommandError
from stack.switch.m7800 import SwitchMellanoxM7800
from stack.switch import SwitchException
from stack.expectmore import ExpectMoreException

class Implementation(stack.commands.Implementation):

	def update_firmware(self, switch_name, firmware_url, downgrade, **kwargs):
		try:
			# connect to the switch and run the firmware upgrade procedure
			m7800_switch = SwitchMellanoxM7800(switch_name, **kwargs)
			m7800_switch.connect()
			# delete all stored images on the switch before sending ours over
			for image in m7800_switch.show_images().images_fetched_and_available:
				m7800_switch.image_delete(image = image.filename)

			m7800_switch.image_fetch(url = firmware_url)
			# install the firmware we just sent to the switch
			m7800_switch.install_firmware(
				# grab the filename from the switch on purpose in case it does something funky with it
				image = m7800_switch.show_images().images_fetched_and_available[0].filename
			)
			# set the switch to boot from our installed image
			m7800_switch.image_boot_next()
			# perform extra downgrade steps if necessary
			if downgrade:
				# need to force a boot, even if the old code parsing the new configuration fails.
				m7800_switch.disable_fallback_reboot()
				m7800_switch.write_configuration()
				m7800_switch.reload()
				# now wait for the switch to come back.
				reconnected = False
				# timeout after 30 minutes. We use a no-op lambda because we just want to know when the timer expired.
				timer = Timer(1800, lambda: ())
				timer.start()
				while timer.is_alive():
					# swallow the expected exceptions while trying to connect to a switch that isn't ready yet.
					with suppress(SwitchException, ExpectMoreException):
						# use the switch as a context manager so every time the connect or factory reset fails,
						# we disconnect from the switch.
						with m7800_switch:
							m7800_switch.connect()
							# now factory reset the switch, which will reboot it again.
							# The successful connect above doesn't seem to guarantee that we can fire a
							# factory reset command, so we try in this loop.
							m7800_switch.factory_reset()
							timer.cancel()
							reconnected = True

				if not reconnected:
					raise CommandError(
						cmd = self.owner,
						msg = f'Unable to reconnect {switch_name} to switch while performing downgrade procedure.'
					)
			else:
				m7800_switch.reload()
		# Turn some potentially verbose and detailed error messages into something more end user friendly
		# while keeping the dirty details available in the logs.
		except (SwitchException, ExpectMoreException) as exception:
			stack.commands.Log(
				message = f'Error during firmware update on {switch_name}: {exception}',
				level = syslog.LOG_ERR
			)
			raise CommandError(
				cmd = self.owner,
				msg = f'Failed to update firmware on {switch_name}.'
			)

	def run(self, args):
		switch_upgrade_args = {}
		# for each switch, build a set of args
		for switch_name_make_model, firmware_info in args.items():
			# There is no currently known valid multi-file use case for mellanox.
			# We don't care if the user tried to force multiple firmware files down our throats.
			if len(firmware_info.firmware_files) > 1:
				raise CommandError(
					self.owner,
					msg = (
						"Firmware update for mellanox switches cannot operate on multiple firmware files at once."
						" Please fix your configuration and try again."
					)
				)
			firmware_file = firmware_info.firmware_files.pop()

			kwargs = {
				'username': firmware_info.host_attrs.get('switch_username', None),
				'password': firmware_info.host_attrs.get('switch_password', None)
			}

			kwargs = {key: value for key, value in kwargs.items() if value is not None}

			notice = f'Syncing firmware {firmware_file.version} for {switch_name_make_model.host}.'
			# check for downgrade as we have to do extra steps
			downgrade = firmware_info.current_version > firmware_file.version
			if downgrade:
				notice += f' This is a downgrade from {firmware_info.current_version} and will perform a factory reset.'
			self.owner.notify(notice)
			# build the args
			switch_upgrade_args[switch_name_make_model.host] = {
				'firmware_url': firmware_file.url,
				'downgrade': downgrade,
				**kwargs,
			}

		errors = []
		# now run each switch upgrade in parallel
		with ThreadPoolExecutor(thread_name_prefix = 'mellanox_firmware_update') as executor:
			futures = [
				executor.submit(self.update_firmware, switch_name = switch_name, **switch_args)
				for switch_name, switch_args in switch_upgrade_args.items()
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
				msg = f"Errors occurred during Mellanox firmware upgrade:\n{error_message}"
			)
