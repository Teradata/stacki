# $Id: __init__.py,v 1.6 2010/12/08 23:04:22 bruno Exp $
# 
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
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
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@
#
# $Log$
# Revision 1.9  2011/08/23 06:17:04  anoop
# Include all zones, not just the last one, when writing the reverse
# map files
#
# Revision 1.8  2011/08/04 03:40:28  anoop
# Bug fixes to named config file generation.
# Now supports subnets that are on non-octet
# boundaries.
# Also supports multiple networks that share
# same/similar classless subnets
# Requires extensive testing
#
# Revision 1.6  2010/12/08 23:04:22  bruno
# for aliases, make sure the format is 'alias CNAME real_host_name'
#
# Revision 1.5  2010/12/08 18:09:28  bruno
# make sure aliases are written as 'c0-1' and not '(c0-1,)'
#
# Revision 1.4  2010/11/17 01:16:33  anoop
# Cleanup of DNS zone file issues.
# Documentation fixed.
#
# Revision 1.3  2010/09/07 23:53:00  bruno
# star power for gb
#
# Revision 1.2  2010/06/30 17:42:41  anoop
# Added doc string
#
# Revision 1.1  2010/06/30 17:37:33  anoop
# Overhaul of the naming system. We now support
# 1. Multiple zone/domains
# 2. Serving DNS for multiple domains
# 3. No FQDN support for network names
#    - FQDN must be split into name & domain.
#    - Each piece information will go to a
#      different table
# Hopefully, I've covered the basics, and not broken
# anything major
#
# Revision 1.16  2009/06/26 19:02:15  bruno
# alias fix.
#
# thanks to Mike Hallock of UIUC for the fix.
#
# Revision 1.15  2009/05/26 23:04:42  bruno
# mo' bugs
#
# Revision 1.14  2009/05/26 21:36:48  bruno
# fix from scott hamilton for subnets that have prefixes larger than 24 bits.
#
# Revision 1.13  2009/05/01 19:07:04  mjk
# chimi con queso
#
# Revision 1.12  2009/03/21 22:22:55  bruno
#  - lights-out install of VM frontends with new node_rolls table
#  - nuked 'site' columns and tables from database
#  - worked through some bugs regarding entities
#
# Revision 1.11  2009/03/13 21:19:16  bruno
# no more riding the shortname
#
# Revision 1.10  2009/03/04 21:31:44  bruno
# convert all getGlobalVar to getHostAttr
#
# Revision 1.9  2008/10/18 00:55:58  mjk
# copyright 5.1
#
# Revision 1.8  2008/09/22 18:34:31  bruno
# vlan fix for the case where a vlan interface is configured with and IP
# but with no hostname
#
# Revision 1.7  2008/08/29 22:12:35  bruno
# fix for reverse.stack.domain.*.local
#
# Revision 1.6  2008/07/22 00:34:41  bruno
# first whack at vlan support
#
# Revision 1.5  2008/03/06 23:41:40  mjk
# copyright storm on
#
# Revision 1.4  2008/02/19 23:20:24  bruno
# katz made me do it.
#
# Revision 1.3  2007/09/14 18:48:24  bruno
# if there is no short name for an appliance, then don't make an alias for
# it in /var/named/stack.domain
#
# Revision 1.2  2007/08/08 22:23:34  bruno
# also import reverse domain local entries
#
# Revision 1.1  2007/08/08 22:14:41  bruno
# moved 'dbreport named' and 'dbreport dns' to rocks command line
#
#

import os
import time
import string
import types
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
	"rocks report script"
	<example cmd='report zones'>
	Prints contents of all the zone config files
	</example>
	<example cmd='report zones | rocks report script'>
	Creates zone config files in /var/named
	</example>
	<related>sync dns</related>
	"""

	def hostlines(self, name, dnszone):

		"Lists the name->IP mappings for all hosts"

		s = ""

		self.db.execute("select n.name, nt.ip, nt.name "+\
			"from subnets s, nodes n, networks nt "	+\
			"where s.dnszone='%s' " % (dnszone)	+\
			"and nt.subnet=s.id and nt.node=n.id")

		for (name, ip, network_name)in self.db.fetchall():

			if ip is None:
				continue

			if network_name is None:
				network_name = name
			
			record = network_name

			s += '%s A %s\n' % (record, ip)

			# Now record the aliases. We always substitute 
			# network names with aliases. Nothing else will
			# be allowed
			self.db.execute('select a.name from aliases a, '+\
				'networks nt where nt.node=a.node and '	+\
				'nt.ip="%s"' % (ip))

			for alias, in self.db.fetchall():
				s += '%s CNAME %s\n' % (alias, record)

		return s

	def hostlocal(self, name, dnszone):
		"Appends any manually defined hosts to domain file"
		
		filename = '/var/named/%s.domain.local' % name
		s = ''
		# If local file exists import from it
		if os.path.isfile(filename):
			s += "\n;Imported from %s\n\n" % filename
			file = open(filename, 'r')
			s += file.read()
			file.close()
		# if it doesn't exist, create a stub file
		else:
			s += "</file>\n"
			s += '<file name="%s" perms="0644">\n' % filename
			s += ';Extra host mappings go here. Example\n'
			s += ';myhost	A	10.1.1.1\n'

		return s

	def writeForward(self, serial, networks):
		for n in networks:
			dnszone = n.dnszone
			name = n.name
			filename = '/var/named/%s.domain' % name
			s = ''
			s += '<file name="%s" perms="0644">\n' % filename
			s += preamble_template % (dnszone, dnszone, serial,
					dnszone, dnszone)
			s += 'ns A 127.0.0.1\n\n'
			s += self.hostlines(name, dnszone)
			s += self.hostlocal(name, dnszone)
			s += '</file>\n'
			self.addOutput('localhost', s)


	def reversehostlines(self, r_sn, s_name):
		"Lists the IP -> name mappings for all hosts. "
		"Handles only IPv4 addresses."

		s = ''
		subnet_len = len(r_sn.split('.'))
		self.db.execute('select nt.name, nt.ip, s.dnszone ' +\
				'from networks nt, subnets s where ' +\
				's.name="%s" ' % (s_name)	+\
				'and nt.subnet=s.id')

		# Remove all elements of the IP address that are
		# present in the subnet. This is done by counting
		# the number of elements in the subnet, and popping
		# that many from the IP address
		for (name, ip, dnszone) in self.db.fetchall():
			if ip is None:
				continue

			if name is None:
				continue

			t_ip = ip.split('.')[subnet_len:]
			t_ip.reverse()
			
			s += '%s PTR %s.%s.\n' % (string.join(t_ip, '.'), name, dnszone)

		#
		# handle reverse local additions
		#
		filename = '/var/named/reverse.%s.domain.%s.local' \
			% (s_name, r_sn)
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

	def writeReverse(self, serial, networks):
		subnet_list = {}
		s = ''
		for n in networks:
			sn = self.getSubnet(n.subnet, n.netmask)
			sn.reverse()
			r_sn = string.join(sn, '.')
			if not subnet_list.has_key(r_sn):
				subnet_list[r_sn] = []
			subnet_list[r_sn].append(n)
			
		for r_sn in subnet_list:
			if len(subnet_list[r_sn]) == 1:
				n = subnet_list[r_sn][0]
				name = n.name
				dnszone = n.dnszone
				hl = self.reversehostlines(r_sn, name)
			else:
				name = ''
				hl = ''
				for nt in subnet_list[r_sn]:
					name += nt.name + '-'
					hl += '; Entries for subnet:%s, zone:%s\n' % \
						(nt.name, nt.dnszone)
					hl += self.reversehostlines(r_sn, nt.name)
					hl += '\n'
				name = name.rstrip('-')
			filename = '/var/named/reverse.%s.domain.%s'\
				% (name, r_sn)
			s += '<file name="%s" perms="0644">\n' % filename
			s += preamble_template % (name, name, serial,
				name, name)
			s += hl

			s += '</file>\n'
		self.addOutput('localhost', s)
			

	def run(self, params, args):
		serial = int(time.time())

		networks = self.getNetworks()
		self.beginOutput()
		self.writeForward(serial, networks)
		self.writeReverse(serial, networks)
		self.endOutput(padChar = '')
