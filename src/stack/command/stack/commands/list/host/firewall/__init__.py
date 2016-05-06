# @SI_Copyright@
#                             www.stacki.com
#                                  v3.1
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


import stack.commands

class Command(stack.commands.NetworkArgumentProcessor,
	stack.commands.list.host.command):
	"""
	List the current firewall rules for the named hosts.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, the 
	firewall rules for all the known hosts are listed.
	</arg>
	"""

	def formatRule(self, rules, name, table, inid, outid, service,
			protocol, chain, action, flags, comment, source):

		if inid == 0:
			network = 'all'
		else:
			network = self.getNetworkName(inid)
		if outid == 0:
			output_network = 'all'
		else:
			output_network = self.getNetworkName(outid)

		rules[name] = (service, table, protocol, chain, action, network,
			output_network, flags, comment, source)


	def run(self, params, args):
		self.beginOutput()

		for host in self.getHostnames(args):
			rules = {}

			# global
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from global_firewall""")

			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(rules, n, tt, i, o, s, p, c, a, f,
					cmt, 'G')

			# os
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from os_firewall where os =
				(select os from nodes where name = '%s')"""
				% (host))

			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(rules, n, tt, i, o, s, p, c, a, f,
					cmt, 'O')

			# appliance
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from appliance_firewall where
				appliance =
				(select appliance from nodes where name = '%s')
				""" % host)
			
			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(rules, n, tt, i, o, s, p, c, a, f,
					cmt, 'A')

			# host
			self.db.execute("""select name, tabletype, insubnet,
				outsubnet, service, protocol, chain, action,
				flags, comment from node_firewall where node =
				(select id from nodes where name = '%s')"""
				% (host))

			for n, tt, i, o, s, p, c, a, f, cmt in self.db.fetchall():
				self.formatRule(rules, n, tt, i, o, s, p, c, a, f,
					cmt, 'H')

			#
			# output the 'ACCEPT' actions first, the 'REJECT'
			# actions last and all the others in the middle
			#
			for n in rules:
				s, tt, p, c, a, i, o, f, cmt, source = rules[n]
				if a == 'ACCEPT':
					self.addOutput(host, (n, tt, s, p, c, a, i,
						o, f, cmt, source))

			for n in rules:
				s, tt, p, c, a, i, o, f, cmt, source = rules[n]
				if a not in [ 'ACCEPT', 'REJECT' ]:
					self.addOutput(host, (n, tt, s, p, c, a, i,
						o, f, cmt, source))

			for n in rules:
				s, tt, p, c, a, i, o, f, cmt, source = rules[n]
				if a == 'REJECT':
					self.addOutput(host, (n, tt, s, p, c, a, i,
						o, f, cmt, source))

		self.endOutput(header=['host', 'name', 'table', 'service',
			'protocol', 'chain', 'action', 'network',
			'output-network', 'flags', 'comment', 'source' ])

