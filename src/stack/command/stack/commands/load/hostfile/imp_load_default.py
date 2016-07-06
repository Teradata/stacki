# @SI_Copyright@
#                             www.stacki.com
#                                  v3.1
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@


import re
import sys
import stack.csv
import stack.commands
from stack.bool import *
from stack.exception import *

class Implementation(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor,
	stack.commands.NetworkArgumentProcessor,
	stack.commands.BoxArgumentProcessor,
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
		self.networks = self.getNetworkNames()
		self.boxes = self.getBoxNames()
		ipRegex = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")

		reader = stack.csv.reader(open(filename, 'rU'))

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
			notes = None

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
					ip = field
					if not ipRegex.match(ip):
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
				elif header[i] == 'notes':
					notes = field
						
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

			if notes:
				if 'notes' not in self.owner.hosts[name].keys():
					self.owner.hosts[name]['notes'] = notes
				else:
					self.owner.hosts[name]['notes'] += \
						', %s' % notes

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
		ips = []
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
				self.owner.interfaces[name][ifaces[0]]['default'] = 'True'
			else:
				#
				# if there is more than one interface for this
				# host, make sure that one of the interfaces
				# is specified as the 'default' interface
				#
				default = False
				multiple_defaults = False
				for interface in ifaces:
					if self.owner.interfaces[name][interface].has_key('default') and str2bool(self.owner.interfaces[name][interface]['default']) == True:
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
				if ip:
#					self.checkIP(ip)
					if ip in ips:
						msg = 'duplicate IP "%s" in the input file' % ip
						raise CommandError(self.owner, msg)

					ips.append(ip)

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

