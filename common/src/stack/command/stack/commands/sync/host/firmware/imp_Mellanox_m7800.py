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
import stack.commands
from stack.switch.m7800 import SwitchMellanoxM7800

class Implementation(stack.commands.Implementation):

	appliance = 'switch'

	def run(self, args):
		switch_name, firmware_file = args

		switch_attrs = self.owner.getHostAttrDict(switch_name)

		kwargs = {
			'username': switch_attrs[switch_name].get('switch_username', None),
			'password': switch_attrs[switch_name].get('switch_password', None)
		}

		kwargs = {key: value for key, value in kwargs.items() if value is not None}

		self.owner.notify(f'Syncing firmware for {switch_name}\n')

		# calculate the URL the switch can pull this image file from
		url = self.getURLtoFirmwares(switch_name = switch_name, firmware_file = firmware_file)
		# connect to the switch and run the firmware upgrade procedure
		m7800_switch = SwitchMellanoxM7800(switch_name, **kwargs)
		m7800_switch.connect()
		# delete all stored images on the switch before sending ours over
		for image in m7800_switch.show_images().images_fetched_and_available:
			m7800_switch.image_delete(image = image.filename)

		m7800_switch.image_fetch(url = url)
		# install the firmware we just sent to the switch
		m7800_switch.install_firmware(
			image = m7800_switch.show_images().images_fetched_and_available[0].filename
		)
		# set the switch to boot from our installed image
		m7800_switch.image_boot_next()
		m7800_switch.reload()

	def getURLtoFirmwares(self, switch_name, firmware_file):
		host_interface_switch = self.owner.call('list.host.interface', [ switch_name ])
		host_interface_frontend = self.owner.call('list.host.interface', [ 'a:frontend' ])

		switch_networks = set(switch['network'] for switch in host_interface_switch)
		frontend_networks = set(frontend['network'] for frontend in host_interface_frontend)
		common_networks = list(switch_networks & frontend_networks)

		if not common_networks:
			return None

		common_network = common_networks[0]
		ip_addr = [ frontend['ip'] for frontend in host_interface_frontend if frontend['network'] in common_network ]

		if not ip_addr:
			return None

		ip_addr = ip_addr[0]
		# remove the /export/stack prefix from the file path, as /install points to /export/stack
		firmware_file = Path().joinpath(*(part for part in firmware_file.parts if part not in ('export', 'stack')))

		return f'http://{ip_addr}/install{firmware_file}'
