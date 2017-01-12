# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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

import string
import stack.commands

class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Create a report that outputs the firewall rules for a host.

	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>
	
	<example cmd='report host firewall compute-0-0'>
	Create a report of the firewall rules for compute-0-0.
	</example>
	"""

	def getPreamble(self, host):
		self.addOutput(host, ':INPUT ACCEPT [0:0]')
		self.addOutput(host, ':FORWARD DROP [0:0]')
		self.addOutput(host, ':OUTPUT ACCEPT [0:0]')

	def printRules(self, host, table, rules):
		if len(rules) == 0 and table != 'filter':
			return
		self.addOutput(host, '*%s' % table)
		if table == 'filter':
			self.getPreamble(host)
		for rule in rules:
			if rule['comment'] != None:
				self.addOutput(host, '# %s' % rule['comment'])
			s = '-A %s' % rule['chain']
			if rule['network'] != 'all' and \
				rule['network'] != None:
				query = "select nt.device from networks nt," +\
					"nodes n, subnets s where " +\
					"s.name='%s' and " % (rule['network']) +\
					"n.name='%s' and " % host +\
					"nt.node=n.id and nt.subnet=s.id"
				rows = self.db.execute(query)
				if rows:
					interface = self.db.fetchone()[0]
					s += ' -i %s' % interface
			if rule['output-network'] != 'all' and \
				rule['output-network'] != None:
				query = "select nt.device from networks nt," +\
					"nodes n, subnets s where " +\
					"s.name='%s' and " % (rule['output-network']) +\
					"n.name='%s' and " % host +\
					"nt.node=n.id and nt.subnet=s.id"
				rows = self.db.execute(query)
				if rows:
					interface = self.db.fetchone()[0]
					s += ' -o %s' % interface
			if rule['protocol'] != 'all' and \
				rule['protocol'] != None:
				s += ' -p %s' % rule['protocol']
			if rule['service'] != 'all' and \
				rule['service'] != None:
				s += ' --dport %s' % rule['service']
			if rule['flags'] != None:
				s += ' %s' % rule['flags']
			s += ' -j %s' % rule['action']

			self.addOutput(host, s)
			self.addOutput(host,'')

		self.addOutput(host,'COMMIT')
				
	def run(self, params, args):
		self.beginOutput()

                hosts = self.getHostnames(args)
		for host in hosts:
			s = '<stack:file stack:name="/etc/sysconfig/iptables" stack:perms="500">'
			self.addOutput(host, s)
			# First, get a list of all rules for every host,
			# fully resolved
			rules = self.call('list.host.firewall',[host])

			# Separate the rules into accept rules, reject rules,
			# and other rules.
			accept_rules = []
			other_rules = []
			reject_rules = []

			while rules:
				rule = rules.pop()
				if rule['action'] == 'ACCEPT':
					accept_rules.append(rule)
				elif rule['action'] == 'REJECT':
					reject_rules.append(rule)
				elif rule['action'] == 'DROP':
					reject_rules.append(rule)
				else:
					other_rules.append(rule)

			# order the rules by ACCEPT, OTHER, and REJECT
			rules = accept_rules + other_rules + reject_rules

			# Separate rules by the tables that they belong to.
			# They can belong to the filter, nat, raw, and mangle tables.
			tables = {}
			tables['filter'] = []
			
			while rules:
				rule = rules.pop(0)
				table = rule['table']
				if not tables.has_key(table):
					tables[table] = []
				tables[table].append(rule)

			# Generate rules for each of the table types
			for tt in ['filter', 'nat', 'raw', 'mangle']:
				# Finally print all the rules that are present
				# in each table. These rules are already sorted
				# so no further sorting is necessary
				if tables.has_key(tt):
					self.printRules(host, tt, tables[tt])

			#
			# default reject rules
			#
			#rule = self.buildRule(None, None, None, '0:1023',
			#	'tcp', 'REJECT', 'INPUT', None, None)
			#self.addOutput(host, rule)

			#rule = self.buildRule(None, None, None, '0:1023',
			#	'udp', 'REJECT', 'INPUT', None, None)
			#self.addOutput(host, rule)

			self.addOutput(host, '</stack:file>')

		self.endOutput(padChar='', trimOwner=(len(hosts) == 1))

