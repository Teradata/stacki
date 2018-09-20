# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import os
import re

#Import all switch packages
from stack.switch.m7800 import SwitchMellanoxM7800

class Implementation(stack.commands.Implementation):

	driver_path = '/export/stack/drivers/'
	appliance = 'switch'

	def run(self, args):
		current_version = None
		available_version = None

		host = args[0]

		switch_info = self.owner.getHostAttrDict(host)
		switch_make = switch_info[host].get('component.make')
		switch_model = switch_info[host].get('component.model')

		available_version = self.getAvailableVersion(host, switch_make, switch_model)
		current_version = self.getCurrentVersion(host, switch_make, switch_model)

		available_version = self.extractVersionNumber(available_version)
		current_version = self.extractVersionNumber(current_version)

		return [current_version, available_version]


	def getAvailableVersion(self, host, make, model):
		files = os.listdir(os.path.join(self.driver_path, self.appliance, make, model))
		if len(files) == 0:
			return None

		files.sort(reverse=True)
		latest_version = os.path.splitext(files[0])[0]
		return latest_version


	def getCurrentVersion(self, host, make, model):
		switch_attrs = self.owner.getHostAttrDict(host)

		kwargs = {
			'username' : switch_attrs[host].get('username'),
			'password' : switch_attrs[host].get('password')
		}

		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		def m7800():
			s = SwitchMellanoxM7800(host, **kwargs)
			s.connect()
			show_images = s.show_images()
			installed_image = show_images['Installed images'][0]['Partition 1']
			s.disconnect()
			return installed_image

		def default():
			return None

		switcher = { 'Mellanoxm7800' : m7800,
		}

		option = make+model
		func = switcher.get(option, default)
		return func()


	def extractVersionNumber(self, text):
		pattern = r'(\d+\.)+(\d+)'
		extraction = re.search(pattern, text)
		return extraction.group()
