# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
import stack.commands
from stack.switch.m7800 import SwitchMellanoxM7800

class Implementation(stack.commands.Implementation):

	def run(self, args):
		host = args
		switch_attrs = self.owner.getHostAttrDict(host)

		kwargs = {
			'username' : switch_attrs[host].get('switch_username', None),
			'password' : switch_attrs[host].get('switch_password', None)
		}

		kwargs = {key: value for key, value in kwargs.items() if value is not None}

		m7800_switch = SwitchMellanoxM7800(host, **kwargs)
		m7800_switch.connect()
		image_listing = m7800_switch.show_images()
		installed_image = image_listing.installed_images[image_listing.last_boot_partition]
		# try to extract the minimal version number from the verbose version string that the switch
		# returns.
		match = re.search(r'(?P<version>(\d+\.)+\d+)', installed_image)
		if match:
			installed_image = match['version']

		m7800_switch.disconnect()
		return installed_image
