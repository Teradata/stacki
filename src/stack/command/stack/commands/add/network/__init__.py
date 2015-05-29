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
# Revision 1.14  2010/09/07 23:52:50  bruno
# star power for gb
#
# Revision 1.13  2010/06/30 17:37:33  anoop
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
# Revision 1.12  2009/06/05 19:56:25  bruno
# make mtu optional
#
# Revision 1.11  2009/06/03 21:28:52  bruno
# add MTU to the subnets table
#
# Revision 1.10  2009/05/01 19:06:55  mjk
# chimi con queso
#
# Revision 1.9  2008/10/18 00:55:48  mjk
# copyright 5.1
#
# Revision 1.8  2008/09/05 20:11:58  bruno
# get rid of sql warning messages when adding a network
#
# Revision 1.7  2008/03/06 23:41:35  mjk
# copyright storm on
#
# Revision 1.6  2007/07/05 17:46:45  bruno
# fixes
#
# Revision 1.5  2007/07/04 01:47:37  mjk
# embrace the anger
#
# Revision 1.4  2007/07/02 19:43:58  bruno
# more params/flags cleanup
#
# Revision 1.3  2007/06/23 03:54:51  mjk
# - first pass at consistency
# - still needs some docstrings
# - argument processors take SQL wildcards
# - add cannot run twice (must use set)
# - dump does sets not just adds
#
# Revision 1.2  2007/06/19 16:42:40  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.1  2007/06/12 01:10:41  mjk
# - 'rocks add subnet' is now 'rocks add network'
# - added set network subnet|netmask
# - added list network
# - other cleanup
#
# Revision 1.2  2007/06/07 21:23:03  mjk
# - command derive from verb.command class
# - default is MustBeRoot
# - list.command / dump.command set MustBeRoot = 0
# - removed plugin non-bugfix
#
# Revision 1.1  2007/05/30 20:10:53  anoop
# Added rocks add subnet - Command adds a subnet to the subnets table
# in the database. Is currently beta


import os
import sys
import types
import string
import stack.commands

class Command(stack.commands.add.command):
	"""
	Add a network to the database. By default both the "public" and
	"private" networks are already defined by Rocks.
		
	<arg type='string' name='name'>
	Name of the new network.
	</arg>
	
	<arg type='string' name='subnet'>
	The IP network address for the new network.
	</arg>

	<arg type='string' name='netmask'>
	The IP network mask for the new network.
	</arg>

	<param type='string' name='subnet'>
	Can be used in place of the subnet argument.
	</param>
	
	<param type='string' name='netmask'>
	Can be used in place of the netmask argument.
	</param>
	
	<param type='string' name='mtu'>
	The MTU for the new network. Default is 1500.
	</param>

	<param type='string' name='dnszone'>
	The Domain name or the DNS Zone name to use
	for all hosts of this particular subnet. Default
	is set to the name of the subnet
	</param>
	
	<param type='boolean' name='servedns'>
	Parameter to decide whether this zone will be
	served by the nameserver on the frontend.
	</param>

	<example cmd='add network optiputer 192.168.1.0 255.255.255.0'>
	Adds the optiputer network address of 192.168.1.0/255.255.255.0.
	</example>

	<example cmd='add network optiputer subnet=192.168.1.0 netmask=255.255.255.0 mtu=9000
		dnszone="optiputer.net" servedns=true'>
	Same as above, but set the MTU to 9000.
	</example>
	"""

        def run(self, params, args):
        	
        	(args, subnet, netmask) = self.fillPositionalArgs(
        		('subnet', 'netmask'))

		(mtu,) = self.fillParams([('mtu', '1500')])

        	if len(args) != 1:
        		self.abort('must supply one network')
        	name = args[0]

		if not subnet:
                        self.abort('subnet not specified')
		if not netmask:
                        self.abort('netmask not specified')

		(dnszone, servedns) = self.fillParams([('dnszone', name),
			('servedns','n')])

		servedns = self.str2bool(servedns)
		# Insert the name of the new network into the subnets
		# table if it does not already exist
			
		rows = self.db.execute("""select * from subnets where 
			name='%s'""" % name)
		if rows > 0:
			self.abort('network "%s" exists' % name)
		
		self.db.execute("""insert into subnets (name, subnet, netmask,
			mtu, dnszone, servedns) values ('%s', '%s', '%s', %s, '%s', %s)"""\
			% (name, subnet, netmask, mtu, dnszone, servedns))

