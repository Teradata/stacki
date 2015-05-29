# $Id: __init__.py,v 1.7 2011/03/23 00:14:55 anoop Exp $
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
# Revision 1.9  2011/08/20 23:11:26  anoop
# Missed checking this in.
#
# Revision 1.7  2011/03/23 00:14:55  anoop
# Added support for subnets in between /8, /16, and /24
#
# Revision 1.6  2010/09/07 23:52:58  bruno
# star power for gb
#
# Revision 1.5  2010/06/30 17:37:33  anoop
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
# Revision 1.4  2009/05/01 19:07:01  mjk
# chimi con queso
#
# Revision 1.3  2008/10/18 00:55:56  mjk
# copyright 5.1
#
# Revision 1.2  2008/03/06 23:41:39  mjk
# copyright storm on
#
# Revision 1.1  2008/01/23 19:05:34  bruno
# can now add kernel boot parameters to the running configuration with the rocks
# command line
#
#

import stack.commands

class command(stack.commands.Command):
	MustBeRoot = 0

	def getNetworks(self):
		networks = []
		db_cmd = 'select name, subnet, netmask, dnszone ' + \
			'from subnets where subnets.servedns = True'
		self.db.execute(db_cmd)
		for n in self.db.fetchall():
			network = stack.util.Struct()
			network.name	=	n[0]
			network.subnet	=	n[1]
			network.netmask	=	n[2]
			network.dnszone	=	n[3]
			networks.append(network)

		return networks
		
		
	def getSubnet_deprecated(self, subnet, netmask):
		s_list = subnet.split('.')
		s_list = map(int, s_list)
		
		n_list = netmask.split('.')
		n_list = map(int, n_list)
		
		net_list = []
		for i in range(0, 4):
			if n_list[i] == 255:
				net_list.append(str(s_list[i]))

		return net_list

	# This Function returns a subnet with a
	# CIDR netmask that is not a multiple of
	# 8. This means subnets smaller than /24 (25-32)
	# will result in the correct subnet being
	# computed for named.conf.
	def getSubnet(self, subnet, netmask):
		s_list = subnet.split('.')
		s_list = map(int, s_list)
		
		n_list = netmask.split('.')
		n_list = map(int, n_list)
		
		net_list = []
		cidr = 0
		for i in range(0, 4):
			if n_list[i] == 0:
				break
			elif n_list[i] == 255:
				net_list.append(str(s_list[i]))
				cidr = cidr + 8
			else:
				b = n_list[i]
				s = 0
				while (b > 0):
					b = (b << 1 ) - 256
					s = s + 1
				s = cidr + s
				net_list.append("%d-%d" % (s_list[i], s))

		return net_list
