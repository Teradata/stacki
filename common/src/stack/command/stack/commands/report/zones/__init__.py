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

import os
import time

import stack.commands
from stack.util import flatten


preamble_template = """$TTL 3D
@ IN SOA ns.%s. root.ns.%s. (
	%s ; Serial
	8H ; Refresh
	2H ; Retry
	4W ; Expire
	1D ) ; Min TTL
;
	NS ns.%s.
	MX 10 mail.%s.

"""


class Command(stack.commands.report.command):
	"""
	Prints out all the named zone.conf and reverse-zone.conf files in XML.
	To actually create these files, run the output of the command through
	"stack report script"

	<example cmd='report zones'>
	Prints contents of all the zone config files
	</example>

	<example cmd='report zones | stack report script'>
	Creates zone config files in /var/named
	</example>

	<related>sync dns</related>
	"""

	def host_lines(self, name, zone):
		"Lists the name->IP mappings for all hosts"

		s = ""
		for (host_name, ip, device, network_name) in self.db.select("""
			nodes.name, networks.ip, networks.device, networks.name
			from subnets, nodes, networks
			where subnets.zone=%s
			and networks.subnet=subnets.id and networks.node=nodes.id
		""", (zone,)):
			if ip is None:
				continue

			if not network_name:
				network_name = host_name

			s += '%s A %s\n' % (network_name, ip)

			# Now record the aliases as CNAMEs
			for alias in flatten(self.db.select("""
				aliases.name from aliases, networks
				where networks.device=%s and networks.id=aliases.network
			""", (device,))):
				s += '%s CNAME %s\n' % (alias, network_name)

		return s

	def host_local(self, name, zone):
		"Appends any manually defined hosts to domain file"

		filename = '%s/%s.domain.local' % (self.named, name)
		s = ''

		# If local file exists import from it
		if os.path.isfile(filename):
			s += "\n;Imported from %s\n\n" % filename
			file = open(filename, 'r')
			s += file.read()
			file.close()
		# If it doesn't exist, create a stub file
		else:
			s += "</stack:file>\n"
			s += '<stack:file stack:name="%s" stack:perms="0644">\n' % filename
			s += ';Extra host mappings go here. Example\n'
			s += ';myhost	A	10.1.1.1\n'

		return s

	def reverse_host_lines(self, r_sn, s_name):
		"""
		Lists the IP -> name mappings for all hosts.
		Handles only IPv4 addresses.
		"""

		s = ''
		subnet_len = len(r_sn.split('.'))

		# Remove all elements of the IP address that are present in
		# the subnet. This is done by counting the number of elements
		# in the subnet, and popping that many from the IP address.
		for (network_name, host_name, ip, zone) in self.db.select("""
			networks.name, nodes.name, networks.ip, subnets.zone
			from networks, subnets, nodes
			where subnets.name=%s
			and networks.subnet=subnets.id and networks.node=nodes.id
		""", (s_name,)):
			if not network_name:
				network_name = host_name

			if ip is None:
				continue

			t_ip = ip.split('.')[subnet_len:]
			t_ip.reverse()

			s += '%s PTR %s.%s.\n' % ('.'.join(t_ip), network_name, zone)

		# Handle reverse local additions
		filename = '%s/reverse.%s.domain.%s.local' % (self.named, s_name, r_sn)
		if os.path.exists(filename):
			s += '\n;Imported from %s\n\n' % filename
			f = open(filename, 'r')
			s += f.read()
			f.close()
			s += '\n'
		else:
			s += '\n'
			s += '; Custom entries for network %s\n' % s_name
			s += '; can be placed in %s\n' % filename
			s += '; These entries will be sourced on sync\n'

		return s

	def run(self, params, args):
		serial = int(time.time())

		networks = []
		for row in self.call('list.network', [ 'dns=true' ]):
			networks.append(row)

		if self.os == 'sles':
			self.named = '/var/lib/named'
		elif self.os == 'redhat':
			self.named = '/var/named'

		self.beginOutput()

		# Forward Lookups
		for network in networks:
			name = network['network']
			zone = network['zone']
			filename = '%s/%s.domain' % (self.named, name)

			s = '<stack:file stack:name="%s" stack:perms="0644">\n' % filename
			s += preamble_template % (zone, zone, serial, zone, zone)
			s += 'ns A 127.0.0.1\n\n'
			s += self.host_lines(name, zone)
			s += self.host_local(name, zone)
			s += '</stack:file>\n'

			self.addOutput('', s)

		# Reverse Lookups
		s = ''
		for network in networks:
			address = network['address']
			mask = network['mask']
			zone = network['zone']
			name = network['network']

			sn = self.getSubnet(address, mask)
			sn.reverse()
			r_sn = '.'.join(sn)
			filename = '%s/reverse.%s.domain.%s' % (self.named, name, r_sn)

			s += '<stack:file stack:name="%s" stack:perms="0644">\n' % filename
			s += preamble_template % (name, name, serial, name, name)
			s += self.reverse_host_lines(r_sn, name)
			s += '</stack:file>\n'

		self.addOutput('', s)
		self.endOutput(padChar='')
