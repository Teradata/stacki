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
import re
import stack.commands
from stack.exception import CommandError
from stack.switch.m7800 import SwitchMellanoxM7800

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
			# TODO: temporary skip
			self.owner.notify(f'Mellanox firmware downgrade not yet supported. Skipping {switch_name}.\n')
			return
		self.owner.notify(notice + '\n')

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
			pass
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
