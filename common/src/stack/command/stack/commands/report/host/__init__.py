# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
import stack.text
import os.path
import shlex


class command(stack.commands.HostArgumentProcessor,
	      stack.commands.report.command):
	pass


class Command(command):
	"""
	Report the host to IP address mapping in the form suitable for
	/etc/hosts.

	<example cmd='report host'>
	Outputs data for /etc/hosts.
	</example>
	"""

	def run(self, param, args):
		self.beginOutput()
		self.addOutput(None, stack.text.DoNotEdit())
		self.addOutput(None, '#  Site additions go in /etc/hosts.local\n')
		self.addOutput(None, '127.0.0.1\tlocalhost.localdomain\tlocalhost\n')
		zones = {}
		aliases = {}

		# Populate the zone map : network->zone
		for row in self.call('list.network'):
			zones[row['network']] = row['zone']

		# Populate the host -> interface -> aliases map
		for row in self.call('list.host.alias'):
			host = row['host']
			interface = row['interface']
			if host not in aliases:
				aliases[host] = {}
			if interface not in aliases[host]:
				aliases[host][interface] = []
			aliases[host][interface].append(row['alias'])

		hosts = {}

		# Get a list of all interface, and populate the host map
		# host -> interfaces.
		# {"hostname":[
		#	{"ip":"1.2.3.4", "interface":"eth0", "zone":"domain.com","default":True/None, "shortname":True/False},
		#	{"ip":"2.3.4.5", "interface":"eth1", "zone":"domain2.com","default":True/None, "shortname":True/False},
		#	]}
		interfaces = self.call('list.host.interface')
		for row in interfaces:
			if not row['ip']:
				continue
			# Each interface dict contains interface name,
			# zone,whether the interface is the default one,
			# and whether the shortname should be assigned
			# to that interface
			host = row['host']
			if host not in hosts:
				hosts[host] = []
			h = {}
			h['ip'] = row['ip']
			h['interface'] = row['interface']
			h['zone'] = zones[row['network']]
			h['default'] = row['default']
			h['shortname'] = False
			if 'options' in row and row['options']:
				options = shlex.split(row['options'])
				for option in options:
					if option.strip() == 'shortname':
						h['shortname']= True
			hosts[host].append(h)


		for host in hosts:
			# Check if any interface for the host has
			# shortname set to true
			shortname_exists = False
			l = list(filter(lambda x: x['shortname'], hosts[host]))
			if len(l):
				shortname_exists = True

			# For each interface in the host, get ip, zone, and names,
			# default, and shortname info
			for row in hosts[host]:
				ip = row['ip']
				zone = row['zone']
				default = row['default']
				interface = row['interface']
				shortname = row['shortname']
				names = []
				# Get the FQDN
				if zone:
					names.append('%s.%s' % (host, zone))
				# If shortname for an interface is set to true,
				# set this interface to have the shortname
				if shortname_exists and shortname:
					names.append(host)
				# If shortname is not set for any interface
				# set the default interface to have the shortname
				if default and not shortname_exists:
					names.append(host)

				# Add any interface specific aliases
				if host in aliases:
					if interface in aliases[host]:
						for alias in aliases[host].get(interface):
							names.append(alias)
				# Write it all
				self.addOutput(None, '%s\t%s' % (ip, ' '.join(names)))


		# Finally, add the hosts.local file to the list
		hostlocal = '/etc/hosts.local'
		if os.path.exists(hostlocal):
			f = open(hostlocal, 'r')
			self.addOutput(None, '\n# Imported from /etc/hosts.local\n')
			h = f.read()
			self.addOutput(None, h)
			f.close()

		self.endOutput(padChar='', trimOwner=True)
