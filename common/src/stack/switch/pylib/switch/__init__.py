# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os


# A custom exception just so its easier to differentiate from Switch exceptions and system ones
class SwitchException(Exception):
	pass

class Switch():
	def __init__(self, switch_ip_address, switchname=None, username=None, password=None):
		# Grab the user supplied info, in case there is a difference (PATCH)
		self.switch_ip_address = switch_ip_address
		self.stacki_server_ip = None

		if switchname:
			self.switchname = switchname
		else:
			self.switchname = 'switch'

		if username:
			self.username = username
		else:
			self.username = 'admin'

		if password:
			self.password = password
		else:
			self.password = 'admin'

		self.tftpdir = '/tftpboot/pxelinux'

		switchdir = '%s/%s' % (self.tftpdir, self.switchname)
		if not os.path.exists(switchdir):
			os.makedirs(switchdir)

		self.current_config = '%s/current_config' % self.switchname
		self.new_config = '%s/new_config' % self.switchname

	def __enter__(self):
		# Entry point of the context manager
		return self

	def __exit__(self, *args):
		try:
			self.disconnect()
		except AttributeError:
			pass
			## TODO: release file lock here

