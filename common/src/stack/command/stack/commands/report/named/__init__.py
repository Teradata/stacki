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

import zlib
import ipaddress
import pathlib
import jinja2

import stack.commands
import stack.commands.report
import stack.text

from stack.exception import CommandError


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

		local_conf = pathlib.Path('/opt/stack/share/templates/named.conf.j2')
		if local_conf.is_file():
			template_file = jinja2.Template(local_conf.read_text(), lstrip_blocks=True, trim_blocks=True)
		else:
			raise CommandError(self, 'Unable to parse template file: /opt/stack/share/templates/named.conf.j2')

		s = '<stack:file stack:name="/etc/named.conf" stack:perms="0644">\n'
		template_vars = {'edit_warning': stack.text.DoNotEdit()}

		acl = ['127.0.0.0/24']
		for network in networks:
			acl.append(str(ipaddress.IPv4Interface(f"{network['address']}/{network['mask']}")))
		template_vars['acl_list'] = acl

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
			template_vars['forwarders'] = ';'.join(fwds.split(','))

		if self.os == 'redhat':
			template_vars.update({
				'directory': '/var/named',
				'dumpfile': '/var/named/data/cache_dump.db',
				'statfile': '/var/named/data/named_stats.txt',
				'hintfile': 'named.ca',
				'localzone': 'named.localhost',
				'loopzone': 'named.local',
			})
		elif self.os == 'sles':
			template_vars.update({
				'directory': '/var/lib/named',
				'dumpfile': '/var/log/named_dump.db',
				'statfile': '/var/log/named.stats',
				'hintfile': 'root.hint',
				'localzone': 'localhost.zone',
				'loopzone': '127.0.0.zone',
			})

		# Generate the Forward Lookups
		fw_zones = []
		for network in networks:
			fw_zones.append({'name': network["network"], 'zone': network["zone"]})
		template_vars['fwzones'] = fw_zones

		# Generate the reverse lookups
		# For every network, get the base subnet,
		# and reverse it. This is the format
		# that named understands
		rev_zones = []
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
			rev_zones.append({'name': name, 'zone': zone, 'comment_name': comment_name})
		template_vars['revzones'] = rev_zones

		# Check if there are local modifications to named.conf
		local_conf = pathlib.Path('/etc/named.conf.local')
		if local_conf.is_file():
			template_vars['local_conf'] = local_conf.read_text()

		s += template_file.render(template_vars)

		s += '</stack:file>\n'

		self.beginOutput()
		self.addOutput('', s)
		self.endOutput(padChar='')
