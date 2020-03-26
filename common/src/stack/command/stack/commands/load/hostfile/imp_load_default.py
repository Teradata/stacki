# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import re
from operator import itemgetter
from itertools import groupby
import ipaddress

import stack.csv
import stack.commands
from stack.bool import str2bool
from stack.exception import CommandError
from stack.commands import ApplianceArgProcessor, BoxArgProcessor, HostArgProcessor, NetworkArgProcessor

class Implementation(
	ApplianceArgProcessor,
	BoxArgProcessor,
	HostArgProcessor,
	NetworkArgProcessor,
	stack.commands.Implementation):

	"""
	Load attributes into the database based on comma-separated formatted
	file.
	"""

	def checkAppliance(self, appliance):
		if appliance not in self.appliances:
			msg = 'appliance "%s" does not exist in the database' \
				% appliance
			raise CommandError(self.owner, msg)

	def checkIP(self, ip):
		for o in self.list_host_interface:
			if o['ip'] == ip:
				msg = 'IP "%s" is already in the database' % ip
				raise CommandError(self.owner, msg)

	def checkMAC(self, mac):
		for o in self.list_host_interface:
			if o['mac'].lower() == mac:
				msg = 'MAC "%s" is already in the database' \
					% mac
				raise CommandError(self.owner, msg)

	def checkNetwork(self, network):
		if network not in self.networks:
			msg = 'network "%s" does not exist in the database' \
				% network
			raise CommandError(self.owner, msg)

	def checkBox(self, box):
		if box not in self.boxes:
			msg = 'box "%s" does not exist in the database' % box
			raise CommandError(self.owner, msg)

	def run(self, args):
		filename, = args

		self.list_host_interface = \
			self.owner.call('list.host.interface')
		self.appliances = self.getApplianceNames()
		# need all the info from networks(/subnets)
		self.networks = dict((k, next(v)) for k, v in groupby(self.owner.call('list.network'), itemgetter('network')))
		self.boxes = self.get_box_names()
		self.actions = [entry['bootaction'] for entry in self.owner.call('list.bootaction')]

		try:
			reader = stack.csv.reader(open(filename, encoding='ascii'))

			header = None
			for row in reader:

				if not header:
					header = row

					#
					# make checking the header easier
					#
					required = [ 'name', 'appliance', 'ip', 'mac',
						'interface', 'rack', 'rank', 'network' ]

					for i in range(0, len(row)):
						if header[i] in required:
							required.remove(header[i])

					if len(required) > 0:
						msg = 'the following required fields are not present in the input file: "%s"' % ', '.join(required)
						raise CommandError(self.owner, msg)

					continue

				name = None
				box = None
				appliance = None
				rack = None
				rank = None
				ip = None
				mac = None
				interface = None
				network = None
				ifhostname = None
				channel = None
				options = None
				vlan = None
				boss = None
				default = None
				comment = None
				installaction = None
				osaction = None
				groups = None

				for i in range(0, len(row)):
					field = row[i]
					if not field:
						continue

					if header[i] == 'name':
						name = field.lower()
					if header[i] == 'box':
						box = field
					if header[i] == 'appliance':
						appliance = field
					elif header[i] == 'rack':
						rack = field
					elif header[i] == 'rank':
						rank = field
					elif header[i] == 'ip':
						try:
							if field == "auto" or ipaddress.IPv4Address(field):
								ip = field
						except:
							msg = 'invalid IP %s in the input file' % ip
							raise CommandError(self.owner, msg)
					elif header[i] == 'mac':
						#
						# make sure the MAC has lowercase
						# letters
						#
						mac = field.lower()
					elif header[i] == 'interface':
						interface = field.lower()
					elif header[i] == 'network':
						network = field.lower()
					elif header[i] == 'interface hostname':
						ifhostname = field.lower()
					elif header[i] == 'channel':
						channel = field
					elif header[i] == 'options':
						options = field
					elif header[i] == 'vlan':
						try:
							vlan = int(field)
						except:
							msg = 'VLAN "%s" must be an integer' % field
							raise CommandError(self.owner, msg)

						if vlan < 1:
							msg = 'VLAN "%s" must be greater than 0' % vlan
							raise CommandError(self.owner, msg)
					elif header[i] == 'boss':
						boss = field
					elif header[i] == 'default':
						default = field
					elif header[i] == 'comment':
						comment = field
					elif header[i] == 'installaction':
						installaction = field
					elif header[i] in [ 'osaction', 'runaction' ]:
						osaction = field
					elif header[i] == 'groups':
						groups = field

				if not name:
					msg = 'empty host name found in "name" column'
					raise CommandError(self.owner, msg)

				if name not in self.owner.hosts.keys():
					self.owner.hosts[name] = {}

				if box:
					self.checkBox(box)
					self.owner.hosts[name]['box'] = box

				if appliance:
					if 'appliance' in self.owner.hosts[name].keys() and \
							self.owner.hosts[name]['appliance'] != appliance:
						msg = 'two different appliance types specified for host "%s"' % name
						raise CommandError(self.owner, msg)

					self.owner.hosts[name]['appliance'] = appliance

				if rack:
					if 'rack' in self.owner.hosts[name].keys() and \
							self.owner.hosts[name]['rack'] != rack:
						msg = 'two different rack numbers specified for host "%s"' % name
						raise CommandError(self.owner, msg)

					self.owner.hosts[name]['rack'] = rack

				if rank:
					if 'rank' in self.owner.hosts[name].keys() and \
							self.owner.hosts[name]['rank'] != rank:
						msg = 'two different rank numbers specified for host "%s"' % name
						raise CommandError(self.owner, msg)

					self.owner.hosts[name]['rank'] = rank

				if not interface:
					continue

				if name not in self.owner.interfaces.keys():
					self.owner.interfaces[name] = {}

				if interface in self.owner.interfaces[name].keys():
					msg = 'interface "%s" already specified for host "%s"' % (interface, name)
					raise CommandError(self.owner, msg)

				self.owner.interfaces[name][interface] = {}

				if default:
					self.owner.interfaces[name][interface]['default'] = default
				if ip:
					if not network:
						raise CommandError(self.owner, 'inclusion of IP requires inclusion of network')
					self.owner.interfaces[name][interface]['ip'] = ip
				if mac:
					self.owner.interfaces[name][interface]['mac'] = mac
				if network:
					self.owner.interfaces[name][interface]['network'] = network
				if ifhostname:
					self.owner.interfaces[name][interface]['ifhostname'] = ifhostname
				if channel:
					self.owner.interfaces[name][interface]['channel'] = channel
				if options:
					self.owner.interfaces[name][interface]['options'] = options
				if vlan:
					self.owner.interfaces[name][interface]['vlan'] = vlan
				if boss:
					self.owner.hosts[name]['boss'] = boss

				if comment:
					if 'comment' not in self.owner.hosts[name].keys():
						self.owner.hosts[name]['comment'] = comment
					else:
						self.owner.hosts[name]['comment'] += \
							', %s' % comment
				if installaction:
					if installaction not in self.actions:
						msg = 'installaction "%s" does not exist in the database' % installaction
						raise CommandError(self.owner, msg)
					else:
						self.owner.hosts[name]['installaction'] = installaction

				if osaction:
					if osaction not in self.actions:
						msg = 'bootaction "%s" does not exist in the database' % osaction
						raise CommandError(self.owner, msg)
					else:
						self.owner.hosts[name]['osaction'] = osaction

				if groups:
					self.owner.hosts[name]['groups'] = groups.split(',')
		except UnicodeDecodeError:
			raise CommandError(self.owner, 'non-ascii character in file')

		#
		# check if the 'Boss' column was set
		#
		thisboss = self.db.getHostname('localhost')
		hasboss = 0
		for name in self.owner.hosts.keys():
			if 'boss' in self.owner.hosts[name]:
				if self.owner.hosts[name]['boss'] == thisboss:
					hasboss = 1
					break

		if hasboss:
			#
			# now remove all hosts not associated with this Boss
			#
			for name in self.owner.hosts.keys():
				if self.owner.hosts[name]['boss'] != thisboss:
					del self.owner.hosts[name]

					for o in self.list_host_interface:
						if o['name'] == name:
							self.owner.call(
								'remove.host',
								[ name ])

		#
		# sanity checks
		#
		macs = []
		ips = {}
		for name in self.owner.hosts.keys():
			#
			# ensure at least one of the host entries has an
			# appliance associated with it
			#
			if 'appliance' not in self.owner.hosts[name].keys():
				msg = 'must supply an appliance type for host "%s"' % (name)
				raise CommandError(self.owner, msg)
			else:
				self.checkAppliance(
					self.owner.hosts[name]['appliance'])

			#
			# 'default' checking
			#
			ifaces = self.owner.interfaces[name].keys()

			#
			# if there is only one interface, make it the default
			#
			if len(ifaces) == 1:
				for interface in ifaces:
					self.owner.interfaces[name][interface]['default'] = 'True'
			else:
				#
				# if there is more than one interface for this
				# host, make sure that one of the interfaces
				# is specified as the 'default' interface
				#
				default = False
				multiple_defaults = False
				for interface in ifaces:
					if 'default' in self.owner.interfaces[name][interface] and str2bool(self.owner.interfaces[name][interface]['default']) is True:
						if not default:
							default = True
						else:
							multiple_defaults = True
				if not default:
					msg = 'host "%s" has multiple interfaces but none of the interfaces are designated as\na "default" interface. add a "default" column to your spreadsheet and\nmark one of the interfaces as "True" in the default column' % name
					raise CommandError(self.owner, msg)

				if multiple_defaults:
					msg = 'host "%s" has more than one interface designated as the "default" interface.\nedit your spreadsheet so that only one interface is the "default".' % name
					raise CommandError(self.owner, msg)

			#
			# interface specific checks
			#
			for interface in self.owner.interfaces[name].keys():
				try:
					ip = self.owner.interfaces[name][interface]['ip']
				except:
					ip = None
				try:
					vlan = self.owner.interfaces[name][interface]['vlan']
				except:
					vlan = 'default'
				if ip:
#					self.checkIP(ip)
					if vlan in ips:
						if ip != 'auto' and ip in ips[vlan]:
							msg = 'duplicate IP "%s" in the input file' % ip
							raise CommandError(self.owner, msg)
					else:
						ips[vlan] = []

					ips[vlan].append(ip)

				try:
					mac = self.owner.interfaces[name][interface]['mac']
				except:
					mac = None
				if mac:
#					self.checkMAC(mac)
					if mac in macs:
						msg = 'duplicate MAC "%s" in the input file' % mac
						raise CommandError(self.owner, msg)

					macs.append(mac)

				try:
					network = self.owner.interfaces[name][interface]['network']
				except:
					network = None
				if network:
					self.checkNetwork(network)

					if ip:
						# check if 'ip' could exist in 'network'
						network_ip, netmask = itemgetter('address', 'mask')(self.networks[network])
						ipnetwork = ipaddress.IPv4Network(network_ip + '/' + netmask)

						# Handle cases where ipaddr = "auto"
						if ip != "auto" and \
							ipaddress.IPv4Address(ip) not in ipnetwork:
							msg = 'IP "%s" is not in the "%s" IP space (%s/%s)' % \
								(ip, network, network_ip, ipnetwork.prefixlen)
							raise CommandError(self.owner, msg)

				#
				# if 'channel' is specified and if it starts
				# with 'bond', make sure there is an interface
				# for this host that matches the the bond value
				#
				if re.match('bond[0-9]+$', interface):
					found = 0
					for iface in self.owner.interfaces[name].keys():
						if 'channel' not in self.owner.interfaces[name][iface].keys():
							continue

						if interface == self.owner.interfaces[name][iface]['channel']:
							found = 1
							break

					if not found:
						msg = 'bonded interface "%s" is specified for host "%s", ' % (interface, name)
						msg += 'but there is no channel "%s" specified for any interface associated with this host' % (interface)
						raise CommandError(self.owner, msg)

