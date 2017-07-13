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
			installaction = o['installaction']
			runaction = o['osaction']
			box = o['box']

		groups = None
		output, = self.call('list.host.group', [host])
		if output['groups']:
			groups = ','.join(output['groups'].split())

		ip = None
		mac = None
		default = None
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
				installaction = None
				runaction = None
				groups = None
				box = None

			ip = o['ip']
			mac = o['mac']
			default = o['default']
			interface = o['interface']
			network = o['network']
			channel = o['channel']
			options = o['options']
			vlan = o['vlan']

			i += 1

			row = [ name, interface_hostname, default, appliance, rack, rank,
				ip, mac, interface, network, channel, options, vlan,
				installaction, runaction, groups, box ]

			csv_w.writerow(row)

	def run(self, params, args):

		header = ['NAME', 'INTERFACE HOSTNAME', 'DEFAULT', 'APPLIANCE', 'RACK', 'RANK',
			'IP', 'MAC', 'INTERFACE', 'NETWORK', 'CHANNEL', 'OPTIONS', 'VLAN',
			'INSTALLACTION', 'RUNACTION', 'GROUPS', 'BOX']

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
