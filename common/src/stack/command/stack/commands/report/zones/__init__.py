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
	def hostlines(self, name, zone):

		"Lists the name->IP mappings for all hosts"

		s = ""

		self.db.execute("select n.name, nt.ip, nt.name " +
			"from subnets s, nodes n, networks nt "	 +
			"where s.zone='%s' " % (zone)	+
			"and nt.subnet=s.id and nt.node=n.id")

		for (name, device, network_name) in self.db.fetchall():

			if device is None:
				continue

			if network_name is None:
				network_name = name
			
			record = network_name

			s += '%s A %s\n' % (record, device)

			# Now record the aliases. We always substitute 
			# network names with aliases. Nothing else will
			# be allowed
			self.db.execute('select a.name from aliases a, ' +
				'networks nt where nt.id=a.network and '	+
				'nt.device="%s"' % (device))

			for alias, in self.db.fetchall():
				s += '%s CNAME %s\n' % (alias, record)

		return s

	def hostlocal(self, name, zone):
		"Appends any manually defined hosts to domain file"
		
		filename = '%s/%s.domain.local' % (self.named, name)
		s = ''
		# If local file exists import from it
		if os.path.isfile(filename):
			s += "\n;Imported from %s\n\n" % filename
			file = open(filename, 'r')
			s += file.read()
			file.close()
		# if it doesn't exist, create a stub file
		else:
			s += "</stack:file>\n"
			s += '<stack:file stack:name="%s" stack:perms="0644">\n' % filename
			s += ';Extra host mappings go here. Example\n'
			s += ';myhost	A	10.1.1.1\n'

		return s

	def reversehostlines(self, r_sn, s_name):
		"Lists the IP -> name mappings for all hosts. "
		"Handles only IPv4 addresses."

		s = ''
		subnet_len = len(r_sn.split('.'))
		self.db.execute('select nt.name, n.name, nt.ip, s.zone ' +
				'from networks nt, subnets s, nodes n where ' +
				's.name="%s" ' % (s_name)	+
				'and nt.subnet=s.id and nt.node=n.id')

		# Remove all elements of the IP address that are
		# present in the subnet. This is done by counting
		# the number of elements in the subnet, and popping
		# that many from the IP address
		for (netname, nodename, ip, zone) in self.db.fetchall():
			if netname:
				name = netname
			else:
				name = nodename
			if ip is None:
				continue

			if name is None:
				continue

			t_ip = ip.split('.')[subnet_len:]
			t_ip.reverse()
			
			s += '%s PTR %s.%s.\n' % ('.'.join(t_ip), name, zone)

		#
		# handle reverse local additions
		#
		filename = '%s/reverse.%s.domain.%s.local' \
			% (self.named, s_name, r_sn)
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

		osname = self.getHostAttr('localhost', 'os')
		if osname == 'sles':
			self.named = '/var/lib/named'
		elif osname == 'redhat':
			self.named = '/var/named'
		self.beginOutput()

		#
		# Forward Lookups
		#

		for network in networks:
			name = network['network']
			zone = network['zone']
			filename = '%s/%s.domain' % (self.named, name)
			s = ''
			s += '<stack:file stack:name="%s" stack:perms="0644">\n' % filename
			s += preamble_template % (zone, zone, serial, zone, zone)
			s += 'ns A 127.0.0.1\n\n'
			s += self.hostlines(name, zone)
			s += self.hostlocal(name, zone)
			s += '</stack:file>\n'
			self.addOutput('', s)

		#    
		# Reverse Lookups
		#
		
		subnet_list = {}
		s = ''
		for network in networks:
			address = network['address']
			mask    = network['mask']
			zone    = network['zone']
			name    = network['network']

			sn = self.getSubnet(address, mask)
			sn.reverse()
			r_sn = '.'.join(sn)

			filename = '%s/reverse.%s.domain.%s' % (self.named, name, r_sn)
			s += '<stack:file stack:name="%s" stack:perms="0644">\n' % filename
			s += preamble_template % (name, name, serial, name, name)
			s += self.reversehostlines(r_sn, name)
			s += '</stack:file>\n'

		self.addOutput('', s)
		self.endOutput(padChar='')
