# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import csv
from io import StringIO

import stack.commands
from stack.commands import HostArgProcessor

class Command(HostArgProcessor, stack.commands.Command):
	"""
	Outputs a network file in CSV format.
	<dummy />
	"""

	def doNetwork(self, csv_w):
		row = []

		output = self.call('list.network')

		for o in output:
			network = o['network']
			zone = o['zone']
			netmask = o['mask']
			mtu = o['mtu']
			dns = o['dns']
			address = o['address']
			gateway = o['gateway']
			pxe = o['pxe']
			row = [ network, address, netmask, gateway, 
				mtu, zone, dns, pxe]

			row = map(lambda x: '' if x == 'None' else x, row)

			csv_w.writerow(row)

	def run(self, params, args):

		header = ['NETWORK', 'ADDRESS', 'MASK', 'GATEWAY', 'MTU', 'ZONE', 'DNS', 'PXE']

		# CSV writer requires fileIO.
		# Setup string IO processing
		csv_f = StringIO()
		csv_w = csv.writer(csv_f)
		csv_w.writerow(header)

		self.doNetwork(csv_w)

		# Get string from StringIO object
		s = csv_f.getvalue().strip()
		csv_f.close()

		self.beginOutput()
		self.addOutput('', s)
		self.endOutput()
