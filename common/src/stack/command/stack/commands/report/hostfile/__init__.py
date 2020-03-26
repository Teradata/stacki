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
	Outputs a host file in CSV format.
	<dummy />
	"""

	def doHost(self, host):

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
			comment       = o['comment']

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
		rows = []
		for o in output:
			if o['name'] != name:
				interface_hostname = o['name']
			else:
				interface_hostname = name

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
				comment = None

			ip = o['ip']
			mac = o['mac']
			default = o['default']
			interface = o['interface']
			network = o['network']
			channel = o['channel']
			options = o['options']
			vlan = o['vlan']

			i += 1
			rows.append([ name, interface_hostname, default, appliance, rack, rank,
				ip, mac, interface, network, channel, options, vlan,
				installaction, osaction, groups, box, comment ])
		return(rows)

	def run(self, params, args):

		header = ['NAME', 'INTERFACE HOSTNAME', 'DEFAULT', 'APPLIANCE', 'RACK', 'RANK',
			  'IP', 'MAC', 'INTERFACE', 'NETWORK', 'CHANNEL', 'OPTIONS', 'VLAN',
			  'INSTALLACTION', 'OSACTION', 'GROUPS', 'BOX', 'COMMENT']

		s = StringIO()
		w = csv.writer(s)
		w.writerow(header)

		for host in self.getHostnames(args):
			for r in self.doHost(host):
				w.writerow(r)

		self.beginOutput()
		self.addOutput('', s.getvalue().strip())
		self.endOutput()
