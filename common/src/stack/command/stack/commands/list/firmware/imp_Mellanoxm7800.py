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
			'username' : switch_attrs[host].get('username'),
			'password' : switch_attrs[host].get('password')
		}

		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		s = SwitchMellanoxM7800(host, **kwargs)
		s.connect()
		show_images = s.show_images()
		next_boot_partition = show_images['next_boot_partition']
		partition_key = 'Partition '+str(next_boot_partition)
		installed_image = show_images['installed_images'][next_boot_partition-1][partition_key]
		s.disconnect()
		return installed_image
