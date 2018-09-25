# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.commands.list.firmware as firm


#Import all switch packages
from stack.switch.m7800 import SwitchMellanoxM7800

class Implementation(stack.commands.Implementation):

	firmware_path = firm.getFirmwarePath()
	appliance = 'switch'

	def run(self, args):
		current_version = None
		available_version = None

		host = args[0]
		switch_info = self.owner.getHostAttrDict(host)
		switch_make = switch_info[host].get('component.make')
		switch_model = switch_info[host].get('component.model')

		available_version = firm.getAvailableVersion(self.appliance, switch_make, switch_model)
		current_version = self.getCurrentVersion(host, switch_make, switch_model)

		available_version= firm.extractVersionNumber(available_version)
		current_version = firm.extractVersionNumber(current_version)

		return [current_version, available_version]


	def getCurrentVersion(self, host, make, model):
		if not make or make == 'None':
			make = ""
		if not model or model == 'None':
			model = ""
		option = make+model
		option = option.replace(" ","")
		return self.owner.runImplementation(option, [host])	

