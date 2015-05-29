# $Id$
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
# Revision 1.5  2011/02/24 20:10:27  bruno
# Added documentation and examples to the add/close/open firewall commands.
# Thanks to Larry Baker for the suggestion.
#
# Revision 1.4  2010/09/07 23:52:49  bruno
# star power for gb
#
# Revision 1.3  2010/05/25 21:23:46  bruno
# more firewall fixes
#
# Revision 1.2  2010/05/07 23:13:32  bruno
# clean up the help info for the firewall commands
#
# Revision 1.1  2010/05/04 22:04:14  bruno
# more firewall commands
#
#

import stack.commands
import stack.commands.add
import stack.commands.add.firewall

class Command(stack.commands.add.firewall.command,
	stack.commands.add.appliance.command):

	"""
	Add a firewall rule for an appliance type.

	<arg type='string' name='appliance'>
	Appliance type (e.g., "compute").
	</arg>

	<param type='string' name='service'>
	The service identifier, port number or port range. For example
	"www", 8080 or 0:1024.
	To have this firewall rule apply to all services, specify the
	keyword 'all'.
	</param>

	<param type='string' name='protocol'>
	The protocol associated with the service. For example, "tcp" or "udp".
	To have this firewall rule apply to all protocols, specify the
	keyword 'all'.
	</param>
	
        <param type='string' name='network'>
        The network for this rule. This is a named network
        (e.g., 'private') and must be one listed by the command
        'rocks list network'.
	To have this firewall rule apply to all networks, specify the
	keyword 'all'.
	</param>

        <param type='string' name='output-network' optional='1'>
        The output network for this rule. This is a named
	network (e.g., 'private') and must be one listed by the command
        'rocks list network'.
	</param>

        <param type='string' name='chain'>
	The iptables 'chain' for this this rule (e.g., INPUT, OUTPUT, FORWARD).
	</param>

        <param type='string' name='action'>
	The iptables 'action' this rule (e.g., ACCEPT, REJECT, DROP).
	</param>

	<param type='string' name='table'>
	The table to add the rule to. Valid values are 'filter',
	'nat', 'mangle', and 'raw'. If this parameter is not
	specified, it defaults to 'filter'
	</param>

	<param type='string' name='rulename'>
	The rule name for the rule to add. This is the handle by
	which the admin can remove or override the rule.
	</param>


	<example cmd='add appliance firewall login network=private service="all" protocol="all" action="ACCEPT" chain="FORWARD"'>
	Accept all services and all protocols on the private network for the
	FORWARD chain.
	If 'eth0' is associated with the private network on a login appliance,
	then this will be translated as the following iptables rule:
	"-A FORWARD -i eth0 -j ACCEPT"
	</example>

	<example cmd='add appliance firewall login network=all service="8649" protocol="udp" action="REJECT" chain="INPUT"'>
	Reject UDP packets with a destination port of 8649 on all networks for
	the INPUT chain.
	On login appliances, this will be translated into the following
	iptables rule:
	"-A INPUT -p udp --dport 8649 -j REJECT"
	</example>
	"""

	def run(self, params, args):
		(service, network, outnetwork, chain, action, protocol, flags,
			comment, table, rulename) = self.fillParams([
				('service', ),
				('network', ),
				('output-network', ),
				('chain', ),
				('action', ),
				('protocol', ),
				('flags', ),
				('comment', ),
				('table','filter'),
				('rulename',),
			])

		if len(args) == 0:
			self.abort('must supply at least one appliance type')

		(service, network, outnetwork,
		chain, action, protocol, flags,
		comment, table, rulename) = self.checkArgs(service, network,
					outnetwork, chain, action, protocol,
					flags, comment, table, rulename)

		apps = self.getApplianceNames(args)

		for app in apps:
			sql = """appliance = (select id from appliances where
				name = '%s') and""" % app

			self.checkRule('appliance_firewall', sql, service,
				network, outnetwork, chain, action, protocol,
				flags, comment, table, rulename)

		#
		# all the rules are valid, now let's add them
		#
		for app in apps:
			sql = """(select id from appliances where
				name='%s'), """ % app

			self.insertRule('appliance_firewall', 'appliance, ',
				sql, service, network, outnetwork, chain,
				action, protocol, flags, comment, table, rulename)

