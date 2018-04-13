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

import ipaddress

import stack.commands
import stack.text

config_preamble_redhat = """options {
	directory "/var/named";
	dump-file "/var/named/data/cache_dump.db";
	statistics-file "/var/named/data/named_stats.txt";
	forwarders { %s; };
	allow-query { private; };
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
	forwarders { %s; };
	allow-query { private; };
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
zone_template = """
zone "%s" {
	type master;
	notify no;
	file "%s.domain";
};

zone "%s.in-addr.arpa" {
	type master;
	notify no;
	file "reverse.%s.domain.%s";
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
		if not fwds:
			#
			# in the case of only one interface on the frontend,
			# then Kickstart_PublicDNSServers will not be
			# defined and Kickstart_PrivateDNSServers will have
			# the correct DNS servers
			#
			fwds = self.getAttr('Kickstart_PrivateDNSServers')

			if not fwds:
				return

		forwarders = ';'.join(fwds.split(','))
		if self.getHostAttr('localhost','os') == 'redhat':
			s += config_preamble_redhat % (forwarders)
		if self.getHostAttr('localhost','os') == 'sles':
			s += config_preamble_sles % (forwarders)

		# For every network, get the base subnet,
		# and reverse it. This is basically the
		# format that named understands

		for network in networks:
			sn = self.getSubnet(network['address'], network['mask'])
			sn.reverse()
			r_sn = '.'.join(sn)
			s += zone_template % (network['zone'],
					      network['network'],
					      r_sn,
					      network['network'],
					      r_sn)

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
