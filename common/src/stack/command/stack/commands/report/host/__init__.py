# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os.path
import shlex

import stack.commands
from stack.commands import HostArgProcessor, Warn
import stack.text


class command(HostArgProcessor, stack.commands.report.command):
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
		text = []
		self.beginOutput()
		text.append('<stack:file stack:name="/etc/hosts">')
		text.append(stack.text.DoNotEdit())
		text.append('#  Site additions go in /etc/hosts.local\n')
		text.append('127.0.0.1\tlocalhost.localdomain\tlocalhost\n')
		zones = {}
		aliases = {}

		# Populate the zone map : network->zone
		for row in self.call('list.network'):
			zones[row['network']] = row['zone']

		# Populate the host -> interface -> aliases map
		for row in self.call('list.host.interface.alias'):
			host = row['host']
			interface = row['interface']
			if host not in aliases:
				aliases[host] = {}
			if interface not in aliases[host]:
				aliases[host][interface] = []
			aliases[host][interface].append(row['alias'])

		hosts = {}

		# Get a list of all interfaces and populate the host map
		# host -> interfaces.
		# {"hostname":[
		#	{"ip":"1.2.3.4", "interface":"eth0", "zone":"domain.com","default":True/None, "shortname":True/False},
		#	{"ip":"2.3.4.5", "interface":"eth1", "zone":"domain2.com","default":True/None, "shortname":True/False},
		#	]}
		interfaces = self.call('list.host.interface')
		for row in interfaces:
			if not row['ip']:
				continue
			if not row['network']:
				Warn(f'WARNING: skipping interface "{row["interface"]}" on host "{row["host"]}" - '
				      'interface has an IP but no network')
				continue

			# Each interface dict contains interface name,
			# zone, whether the interface is the default one,
			# and whether the shortname should be assigned
			# to that interface
			host = row['host']
			if host not in hosts:
				hosts[host] = []
			h = {}
			h['ip'] = row['ip']
			h['name'] = row['name']
			h['interface'] = row['interface']
			h['zone'] = zones[row['network']]
			h['default'] = row['default']
			h['shortname'] = False
			if 'options' in row and row['options']:
				options = shlex.split(row['options'])
				for option in options:
					if option.strip() == 'shortname':
						h['shortname']= True

			if self.validateHostInterface(host, h, aliases):
				hosts[host].append(h)

		processed = {}

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

					if row['name']:
						name_fqdn = f"{row['name']}.{zone}"
						if name_fqdn not in names:
							names.append(name_fqdn)

				# If shortname for an interface is set to true,
				# set this interface to have the shortname
				if shortname_exists and shortname:
					names.append(host)

					if row['name'] and row['name'] not in names:
						names.append(row['name'])

				# If shortname is not set for any interface
				# set the default interface to have the shortname
				if default and not shortname_exists:
					names.append(host)

					if row['name'] and row['name'] not in names:
						names.append(row['name'])

				# Add any interface specific aliases
				if host in aliases:
					if interface in aliases[host]:
						for alias in aliases[host].get(interface):
							names.append(alias)

				# check if this is duplicate entry:
				if ip in processed:
					if processed[ip]['names'] == ' '.join(names):
						continue

				# Write it all
				text.append('%s\t%s' % (ip, ' '.join(names)))

				if ip not in processed:
					processed[ip] = {}
				processed[ip]['names'] = '\t'.join(names)

		# Finally, add the hosts.local file to the list
		hostlocal = '/etc/hosts.local'
		if os.path.exists(hostlocal):
			f = open(hostlocal, 'r')
			text.append('\n# Imported from /etc/hosts.local\n')
			h = f.read()
			text.append(h)
			f.close()

		text.append('</stack:file>')
		self.addOutput(None, '\n'.join(text))
		self.endOutput(padChar='', trimOwner=True)



	def validateHostInterface(self, hostname, hostinfo ,aliases):
	# Checks if a host interface has atleast one of the following:
		#       has an aliases
		if hostname in aliases and hostinfo['interface'] in aliases[hostname]:
			return True
		
		#       is on a network with a zone
		if hostinfo['zone']:
			return True
		
		#       has a shortname option
		if hostinfo['shortname']:
			return True

		#       is the default interface for that host
		if hostinfo['default']:
			return True
		return False
