# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.commands.list.firmware as firm
import os

class command(stack.commands.HostArgumentProcessor, stack.commands.sync.command):
	pass


class Command(command):
	"""
	Updates the firmware of different appliances based on whether a updated version is available in /export/stack/drivers/make/model/

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='sync firmware backend-0-0'>
	Updates backend-0-0.
	</example>

	<example cmd='sync firmware'>
	Updates all known hosts(firmwares).
	</example>
	"""
	
	def run(self, params, args):
		self.notify('Sync Firmware\n')

		firmwares = self.getHostnames(args)

		for firmware in firmwares:
			make = self.getHostAttr(firmware, 'component.make')
			model = self.getHostAttr(firmware, 'component.model')
			firmware_info = self.call('list.firmware',[firmware])[0]
			curr_version = firmware_info['Current Version']
			avail_version = firmware_info['Available Version']
			if not avail_version:
				continue
			if not curr_version:
				continue
			if firm.compareVersion(curr_version, avail_version) >= 0:
				continue

			self.runImplementation(model, [firmware, make, model, avail_version])


def getImageName(appliance, make, model, version):
	if not make or make == 'None':
		make = ""
	if not model or model == 'None':
		model = ""
	files = os.listdir(os.path.join(firm.getFirmwarePath(), appliance, make, model))
	for filename in files:
		if firm.extractVersionNumber(filename) == version:
			return filename
	return None
