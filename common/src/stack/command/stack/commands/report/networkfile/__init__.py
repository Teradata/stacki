# @SI_COPYRIGHT@
# @SI_COPYRIGHT@

import stack.commands
import csv
from io import StringIO


class Command(stack.commands.Command, stack.commands.HostArgumentProcessor):
	"""
	Outputs a network file in CSV format.
	<dummy />
	"""

	def run(self, params, args):

		header = ['NETWORK', 'ADDRESS', 'MASK', 'GATEWAY', 'MTU', 'ZONE', 'DNS', 'PXE']

		s = StringIO()
		w = csv.writer(s)
		w.writerow(header)

		for row in self.call('list.network'):
			network = row['network']
			zone    = row['zone']
			netmask = row['mask']
			mtu     = row['mtu']
			dns     = row['dns']
			address = row['address']
			gateway = row['gateway']
			pxe     = row['pxe']

			w.writerow([ network, address, netmask, gateway, mtu, zone, dns, pxe])

		self.beginOutput()
		self.addOutput(None, s.getvalue().strip())
		self.endOutput()
