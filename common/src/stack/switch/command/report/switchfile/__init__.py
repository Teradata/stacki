# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import csv
from io import StringIO


class Command(stack.commands.Command, stack.commands.HostArgumentProcessor):
	"""
	Outputs a switchfile in CSV format.
	<dummy />
	"""

	def doSwitch(self, switch):
		switch_name	= switch['switch']
		rack		= switch['rack']
		rank		= switch['rank']
		appliance	= switch['appliance']
		model		= switch['model']

		rows = []
		for index, interface in enumerate(self.call('list.host.interface', [ switch_name ])):
			
			if interface['name'] != switch_name:
				interface_hostname = interface['name']
			else:
				interface_hostname = switch_name

			#
			# if host has more than one interface,
			# don't print redundant information.
			#
			if index > 0:
				_username = None
				_password = None

			_interface	= interface['interface']
			_ip		= interface['ip']
			_mac		= interface['mac']
			_network	= interface['network']
			_username	= self.getHostAttr(switch_name, 'switch_username')
			_password	= self.getHostAttr(switch_name, 'switch_password')

			rows.append([
				switch_name,
				rack,
				rank,
				model,
				_interface,
				_ip,
				_mac,
				_network,
				_username,
				_password,
				])


		return rows

	def run(self, params, args):

		header = [
			"NAME",
			"RACK",
			"RANK",
			"MODEL",
			"INTERFACE",
			"IP",
			"MAC",
			"NETWORK",
			"USERNAME",
			"PASSWORD",
			]

		s = StringIO()
		w = csv.writer(s)
		w.writerow(header)

		for switch in self.call('list.switch'):
			for r in self.doSwitch(switch):
				w.writerow(r)

		self.beginOutput()
		self.addOutput('', s.getvalue().strip())
		self.endOutput()
