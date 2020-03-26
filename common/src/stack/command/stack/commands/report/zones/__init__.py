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

##
## Code in this command generates multiple Zone files, one for each network.
## The exception to this is when addressing multiple adjecent networks on
## on non-octet boundaries. For example 39.80/12 and 39.96/12. These are
## distinct, adjecent networks on non-octet boundaries.
## For explanation of how this is designed, look at the Design comment in
## the "stack.report.named" command file.
##

import os
import time
import zlib

import stack.commands
from stack.commands import HostArgProcessor
import stack.commands.report
from stack.util import flatten


preamble_template = """$TTL 3D
@ IN SOA %s. root.%s. (
	%s ; Serial
	8H ; Refresh
	2H ; Retry
	4W ; Expire
	1D ) ; Min TTL
;
	NS %s.
	MX 10 %s.

"""


class Command(HostArgProcessor, stack.commands.report.command):
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

	def run(self, params, args):

		self.frontend = self.getHostnames(["a:frontend"])[0]
		if self.os == 'sles':
			self.named = '/var/lib/named'
		elif self.os == 'redhat':
			self.named = '/var/named'

		networks = self.call('list.network', [ 'dns=true' ])
		hosts = self.call("list.host.interface", ["expanded=true"])
		aliases = self.call("list.host.interface.alias")

		zones = []
		for network in networks:
			n = dict.copy(network)
			sn = self.getSubnet(network["address"],network["mask"])
			sn.reverse()
			r_sn = '.'.join(sn)

			n["hosts"] = self.getHosts(network, hosts, aliases)
			n["reverse_subnet"] = r_sn
			zones.append(n)

		self.beginOutput()
		self.getForwardZones(zones)
		self.getReverseZones(zones)
		self.endOutput()

	def getHosts(self, network, hosts, aliases):
		h = []
		for host in hosts:
			if host["network"] == network["network"]:
				host_record = {
					"name"	: host["host"],
					"ip"	: host["ip"],
					"aliases":[]
					}
				for alias in aliases:
					if alias["host"] == host["host"] and \
						alias["interface"] == host["interface"]:
						host_record["aliases"].append(alias["alias"])
				h.append(host_record)
		return h

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

	def getForwardZones(self, zones):
		serial = int(time.time())
		for network in zones:
			name = network['network']
			zone = network['zone']
			filename = '%s/%s.domain' % (self.named, name)

			s = '<stack:file stack:name="%s" stack:perms="0644">\n' % filename
			s += preamble_template % (self.frontend, self.frontend, serial, self.frontend, self.frontend)
			#s += 'ns A 127.0.0.1\n\n'
			for host in network["hosts"]:
				if host["ip"]:
					s += "%s A %s\n" % (host["name"], host["ip"])
				for alias in host["aliases"]:
					s += "%s CNAME %s\n" % (alias, host["name"])
			s += self.host_local(name, zone)
			s += '</stack:file>\n'

			self.addOutput('', s)


	def getReverseZones(self, zones):
		# Group by reverse zones
		serial = int(time.time())
		z = {}
		for x in zones:
			r_sn = x["reverse_subnet"]
			if not r_sn in z:
				z[r_sn] = []
			z[r_sn].append(x)

		s = ''
		for zone in z:
			if len(z[zone]) == 1:
				name = z[zone][0]["network"]
			else:
				# Generate a CRC32 HEX String from the network names.
				# First, Join the network names using "."
				# Then generate the CRC32 number, and convert it to a
				# positive integer. The convert that integer to HEX
				# Use the HEX String as a Unique key.
				# Given that the this key is used as the name of network,
				# hash collisions are a low probability
				n = '.'.join(list(map(lambda x: x["network"], z[zone]))).encode()
				name = hex(zlib.crc32(n) & 0xffffffff)[2:]
			filename = '%s/reverse.%s.domain' % (self.named, name)

			s += '<stack:file stack:name="%s" stack:perms="0644">\n' % filename
			s += preamble_template % (self.frontend, self.frontend, serial, self.frontend, self.frontend)
			sn_len = len(zone.split("."))
			for l in z[zone]:
				for host in l["hosts"]:
					if not host["ip"]:
						continue
					ip = host["ip"].split(".")
					trunc_ip = ip[sn_len:]
					trunc_ip.reverse()
					s += '%s IN PTR %s.%s.\n' % ('.'.join(trunc_ip), host["name"], l["zone"])

				# Handle reverse local additions
				filename = '%s/reverse.%s.domain.local' % (self.named, l["network"])
				if os.path.exists(filename):
					s += '\n;Imported from %s\n\n' % filename
					f = open(filename, 'r')
					s += f.read()
					f.close()
					s += '\n'
				else:
					s += '\n'
					s += '; Custom entries for the "%s" network\n' % l["network"]
					s += '; can be placed in %s\n' % filename
					s += '; These entries will be sourced on sync\n\n\n'

			s += '</stack:file>\n'
		self.addOutput('', s)
