# @SI_COPYRIGHT@
# @SI_COPYRIGHT@

import stack.commands
import string
import csv
import cStringIO

class Command(stack.commands.Command, stack.commands.HostArgumentProcessor):
	"""
	Outputs a host file in CSV format.
	<dummy />
	"""

	def doHost(self, host, csv_w):
		row = []

		name = host
		interface_hostname = None

		output = self.call('list.host', [ host ])
		for o in output:
			appliance = o['appliance']
			rack = o['rack']
			rank = o['rank']

		ip = None
		mac = None
		interface = None
		network = None
		channel = None
		options = None
		vlan = None

		output = self.call('list.host.interface', [ host ])
		i = 0
		for o in output:
			if o['name'] != name:
				interface_hostname = o['name']
			else:
				interface_hostname = None

			if i > 0:
				#
				# only output these once
				# 
				appliance = None
				rack = None
				rank = None

			ip = o['ip']
			mac = o['mac']
			interface = o['interface']
			network = o['network']
			channel = o['channel']
			options = o['options']
			vlan = o['vlan']

			i += 1

			row = [ name, interface_hostname, appliance, rack,
				rank, ip, mac, interface, network, channel,
				options, vlan ]

			csv_w.writerow(row)

	def run(self, params, args):

		header = ['NAME', 'INTERFACE HOSTNAME', 'APPLIANCE', 'RACK',
			'RANK', 'IP', 'MAC', 'INTERFACE', 'NETWORK',
			'CHANNEL', 'OPTIONS', 'VLAN']

		# CSV writer requires fileIO.
		# Setup string IO processing
		csv_f = cStringIO.StringIO()
		csv_w = csv.writer(csv_f)
		csv_w.writerow(header)

		for host in self.getHostnames(args):
			self.doHost(host, csv_w)

		# Get string from StringIO object
		s = csv_f.getvalue().strip()
		csv_f.close()

		self.beginOutput()
		self.addOutput('',s)
		self.endOutput()
