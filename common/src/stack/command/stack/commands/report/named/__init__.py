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


#####
	## Design for address spaces with non-octet boundary netmasks
	## Read RFC 2317 for more details about requirements.
	##
	## If we have 2 networks, 39.80/12, and 39.96/12, generating
	## zone files for these is very tricky. To do this we club the
	## 2 zones into a single file with 39 as the reverse prefix,
	## and enter the last 3 octets of all IP addresses in both
	## networks into the file.
	##
	## We also need a name for this file. To get a unique name,
	## we put the names of all the networks together - joined by
	## a ".", get the CRC32 string of the new name, and then get
	## the hex value of the CRC32 code.
#####

import os

import ipaddress

import stack.commands
import stack.commands.report
import stack.text
import zlib

config_preamble_redhat = """options {
	directory "/var/named";
	dump-file "/var/named/data/cache_dump.db";
	statistics-file "/var/named/data/named_stats.txt";
	allow-query { private; };
	%s
};

controls {
	inet 127.0.0.1 allow { localhost; } keys { rndc-key; };
};

zone "." IN {
	type hint;
	file "named.ca";
};

zone "localhost" IN {
	type master;
	file "named.localhost";
	allow-update { none; };
};

zone "0.0.127.in-addr.arpa" IN {
	type master;
	file "named.local";
	allow-update { none; };
};
"""

config_preamble_sles = """options {
	directory "/var/lib/named";
	dump-file "/var/log/named_dump.db";
	statistics-file "/var/log/named.stats";
	allow-query { private; };
	%s
};

controls {
	inet 127.0.0.1 allow { localhost; } keys { rndc-key; };
};

zone "." IN {
	type hint;
	file "root.hint";
};

zone "localhost" IN {
	type master;
	file "localhost.zone";
	allow-update { none; };
};

zone "0.0.127.in-addr.arpa" IN {
	type master;
	file "127.0.0.zone";
	allow-update { none; };
};
"""
# zone mapping
fw_zone_template = """
# Zone Mapping for %s
zone "%s" {
	type master;
	notify no;
	file "%s.domain";
};
"""
rev_zone_template = """
# Reverse Zone mapping for %s
zone "%s.in-addr.arpa" {
	type master;
	notify no;
	file "reverse.%s.domain";
};
"""


class Command(stack.commands.report.command):
	"""
	Prints the nameserver daemon configuration file
	for the system.

	<example cmd="report named">
	Outputs /etc/named.conf
	</example>
	"""

	def run(self, params, args):

		networks = []
		for row in self.call('list.network', [ 'dns=true' ]):
			networks.append(row)

		s = '<stack:file stack:name="/etc/named.conf" stack:perms="0644">\n'
		s += stack.text.DoNotEdit()
		s += '# Site additions go in /etc/named.conf.local\n\n'


		acl = [ '127.0.0.0/24']
		for network in networks:
			ipnetwork = ipaddress.IPv4Network(network['address'] + '/' + network['mask'])
			cidr = ipnetwork.prefixlen
			acl.append('%s/%s' % (network['address'], cidr))
		s += 'acl private {\n\t%s;\n};\n\n' % ';'.join(acl)


		fwds = self.getAttr('Kickstart_PublicDNSServers')
		if fwds is None:
			#
			# in the case of only one interface on the frontend,
			# then Kickstart_PublicDNSServers will not be
			# defined and Kickstart_PrivateDNSServers will have
			# the correct DNS servers
			#
			fwds = self.getAttr('Kickstart_PrivateDNSServers')
		if fwds is not None:
			fwds = fwds.strip()
	
		if fwds:
			forwarders = 'forwarders { %s; };' % ';'.join(fwds.split(','))
		else:
			forwarders = ''

		if self.getHostAttr('localhost','os') == 'redhat':
			s += config_preamble_redhat % (forwarders)
		if self.getHostAttr('localhost','os') == 'sles':
			s += config_preamble_sles % (forwarders)

		# Generate the Forward Lookups
		for network in networks:
			s += fw_zone_template % ("%s network" % network["network"],
				network['zone'], network['network'])

		# Generate the reverse lookups
		# For every network, get the base subnet,
		# and reverse it. This is the format
		# that named understands
		z = {}
		for network in networks:
			sn = self.getSubnet(network['address'], network['mask'])
			sn.reverse()
			r_sn = '.'.join(sn)
			if not r_sn in z:
				z[r_sn] = []
			z[r_sn].append(network)
		for zone in z:
			if len(z[zone]) == 1:
				name = z[zone][0]["network"]
				comment_name = name
			else:
				n = '.'.join(list(map(lambda x: x["network"], z[zone]))).encode()
				name = hex(zlib.crc32(n) & 0xffffffff)[2:]
				comment_name = "networks - %s" % ','.join(list(map(lambda x: x["network"], z[zone])))
			s += rev_zone_template % ("%s" % comment_name, zone, name)

		# Check if there are local modifications to named.conf
		if os.path.exists('/etc/named.conf.local'):
			f = open('/etc/named.conf.local', 'r')
			s += '\n#Imported from /etc/named.conf.local\n'
			s += f.read()
			f.close()
			s += '\n'

		s += '\ninclude "/etc/rndc.key";\n'
		s += '</stack:file>\n'

		self.beginOutput()
		self.addOutput('', s)
		self.endOutput(padChar='')
