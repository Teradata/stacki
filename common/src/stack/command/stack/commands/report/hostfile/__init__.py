# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import stack.commands
import string
import csv
from io import StringIO

class Command(stack.commands.Command, stack.commands.HostArgumentProcessor):
	"""
	Outputs a host file in CSV format.
	<dummy />
	"""

	def doHost(self, host):
		row = []

		name = host
		interface_hostname = None

		output = self.call('list.host', [ host ])
		for o in output:
			appliance     = o['appliance']
			rack          = o['rack']
			rank          = o['rank']
			installaction = o['installaction']
			osaction      = o['osaction']
			box           = o['box']

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
				osaction = None
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
			
			return [ name, interface_hostname, default, appliance, rack, rank,
				 ip, mac, interface, network, channel, options, vlan,
				 installaction, osaction, groups, box ]


	def run(self, params, args):

		header = ['NAME', 'INTERFACE HOSTNAME', 'DEFAULT', 'APPLIANCE', 'RACK', 'RANK',
			  'IP', 'MAC', 'INTERFACE', 'NETWORK', 'CHANNEL', 'OPTIONS', 'VLAN',
			  'INSTALLACTION', 'OSACTION', 'GROUPS', 'BOX']

		s = StringIO()
		w = csv.writer(s)
		w.writerow(header)

		for host in self.getHostnames(args):
			w.writerow(self.doHost(host))

		self.beginOutput()
		self.addOutput(None, s.getvalue().strip())
		self.endOutput()
