# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.switch.m7800 import SwitchMellanoxM7800

class Implementation(stack.commands.Implementation):

	def run(self, args):
		host = args[0]
		switch_attrs = self.owner.getHostAttrDict(host)

		kwargs = {
			'username' : switch_attrs[host].get('switch_username'),
			'password' : switch_attrs[host].get('switch_password')
		}

		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		m7800_switch = SwitchMellanoxM7800(host, **kwargs)
		m7800_switch.connect()
		image_listing = m7800_switch.show_images()
		installed_image = image_listing.installed_images[image_listing.next_boot_partition]
		m7800_switch.disconnect()
		return installed_image
