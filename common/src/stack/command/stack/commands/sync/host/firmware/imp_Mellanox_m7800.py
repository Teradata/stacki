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

from pathlib import Path
from threading import Timer
from contextlib import suppress
import stack.commands
from stack.exception import CommandError
from stack.switch.m7800 import SwitchMellanoxM7800
from stack.switch import SwitchException
from stack.expectmore import ExpectMoreException

class Implementation(stack.commands.Implementation):

	appliance = 'switch'

	def run(self, args):
		switch_name, current_firmware_version, firmware_file, firmware_file_version = args

		switch_attrs = self.owner.getHostAttrDict(switch_name)

		kwargs = {
			'username': switch_attrs[switch_name].get('switch_username', None),
			'password': switch_attrs[switch_name].get('switch_password', None)
		}

		kwargs = {key: value for key, value in kwargs.items() if value is not None}

		notice = f'Syncing firmware {firmware_file_version} for {switch_name}.'
		# check for downgrade as we have to do extra steps
		downgrade = current_firmware_version > firmware_file_version
		if downgrade:
			notice += f' This is a downgrade from {current_firmware_version} and will perform a factory reset.'
		self.owner.notify(notice)

		# calculate the URL the switch can pull this image file from
		url = self.get_frontend_url(switch_name = switch_name, firmware_file = firmware_file)
		# connect to the switch and run the firmware upgrade procedure
		m7800_switch = SwitchMellanoxM7800(switch_name, **kwargs)
		m7800_switch.connect()
		# delete all stored images on the switch before sending ours over
		for image in m7800_switch.show_images().images_fetched_and_available:
			m7800_switch.image_delete(image = image.filename)

		m7800_switch.image_fetch(url = url)
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
			# timeout after 10 minutes. We use a no-op lambda because we just want to know when the timer expired.
			timer = Timer(600, lambda: ())
			timer.start()
			while timer.is_alive():
				# swallow the expected exceptions while trying to connect to a switch that isn't ready yet.
				with suppress(SwitchException, ExpectMoreException):
					# use the switch as a context manager so every time the connect or factory reset fails,
					# we disconnect from the switch.
					with m7800_switch:
						m7800_switch.connect()
						# now factory reset the switch, which will reboot it again.
						# The successful connect above doesn't seem to guarantee that we can fire a factory reset command,
						# so we try in this loop. The connect is a no-op if we are already connected.
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

	def get_frontend_url(self, switch_name, firmware_file):
		host_interface_frontend = self.owner.call('list.host.interface', ['a:frontend'])

		switch_networks = set(switch['network'] for switch in self.owner.call('list.host.interface', [switch_name]))
		frontend_networks = set(frontend['network'] for frontend in host_interface_frontend)
		common_networks = list(switch_networks & frontend_networks)

		if not common_networks:
			raise CommandError(
				cmd = self.owner,
				msg = (f'{switch_name} does not share a network with the frontend, and thus cannot fetch firmware'
					   f' from it. Please configure {switch_name} to share a common network with the frontend.')
			)

		ip_addr = [
			frontend['ip'] for frontend in host_interface_frontend
			if frontend['network'] in common_networks and frontend['ip']
		]

		if not ip_addr:
			raise CommandError(
				cmd = self.owner,
				msg = (f'None of the network interfaces on the frontend attached to the following common networks'
					   f'have an IP address. Please configure at least one interface to have an IP address on one'
					   f'of the following networks: {common_networks}')
			)

		ip_addr = ip_addr[0]
		# remove the /export/stack prefix from the file path, as /install points to /export/stack
		firmware_file = Path().joinpath(*(part for part in firmware_file.parts if part not in ('export', 'stack')))

		return f'http://{ip_addr}/install{firmware_file}'
