# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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

		self.db.execute("select n.name, nt.ip, nt.name "+\
			"from subnets s, nodes n, networks nt "	+\
			"where s.zone='%s' " % (zone)	+\
			"and nt.subnet=s.id and nt.node=n.id")

		for (name, ip, network_name) in self.db.fetchall():

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

	def hostlocal(self, name, zone):
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
		self.db.execute('select nt.name, nt.ip, s.zone ' +\
				'from networks nt, subnets s where ' +\
				's.name="%s" ' % (s_name)	+\
				'and nt.subnet=s.id')

		# Remove all elements of the IP address that are
		# present in the subnet. This is done by counting
		# the number of elements in the subnet, and popping
		# that many from the IP address
		for (name, ip, zone) in self.db.fetchall():
			if ip is None:
				continue

			if name is None:
				continue

			t_ip = ip.split('.')[subnet_len:]
			t_ip.reverse()
			
			s += '%s PTR %s.%s.\n' % (string.join(t_ip, '.'), name, zone)

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


	def run(self, params, args):
		serial = int(time.time())

                networks = []
                for row in self.call('list.network', [ 'dns=true' ]):
                        networks.append(row)
                        
		self.beginOutput()

                #
                # Forward Lookups
                #

                for network in networks:
                        name = network['network']
                        zone = network['zone']
			filename = '/var/named/%s.domain' % name
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
			r_sn = string.join(sn, '.')

			filename = '/var/named/reverse.%s.domain.%s' % (name, r_sn)
			s += '<stack:file stack:name="%s" stack:perms="0644">\n' % filename
			s += preamble_template % (name, name, serial, name, name)
			s += self.reversehostlines(r_sn, name)
			s += '</stack:file>\n'

		self.addOutput('', s)
		self.endOutput(padChar = '')
