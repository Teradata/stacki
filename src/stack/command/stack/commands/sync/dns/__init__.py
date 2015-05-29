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
# Revision 1.9  2010/09/07 23:53:03  bruno
# star power for gb
#
# Revision 1.8  2010/06/30 17:37:33  anoop
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
# Revision 1.7  2009/05/29 16:51:42  phil
# Eliminate the 2+ second hole where named was down. Replace service restart with service reload.
#
# Revision 1.6  2009/05/01 19:07:04  mjk
# chimi con queso
#
# Revision 1.5  2009/01/13 23:11:33  bruno
# add full pathname to 'service' command so folks can run insert-ethers via
# sudo.
#
# Revision 1.4  2008/10/18 00:55:58  mjk
# copyright 5.1
#
# Revision 1.3  2008/03/06 23:41:40  mjk
# copyright storm on
#
# Revision 1.2  2007/08/09 21:27:40  bruno
# make sure the subnet list is a list of lists
#
# Revision 1.1  2007/08/08 22:14:41  bruno
# moved 'dbreport named' and 'dbreport dns' to rocks command line
#
# Revision 1.1  2007/07/02 18:41:01  bruno
# added 'rocks sync config' (insert-ethers --update) and more sync cleanup
#
#

import os
import sys
import string
import stack.file
import stack.commands


class Command(stack.commands.sync.command):
	"""
	Rebuild the DNS configuration files, then restart named.

	<example cmd='sync dns'>
	Rebuild the DNS configuration files, then restart named.
	</example>
	"""

	def getNetwork(self):
		"Returns the network address of this cluster"

		self.db.execute("""select subnet from subnets where
			name = 'private'""")
		network, = self.db.fetchone()
		
		return network


	def getNetmask(self, net):
		"Determines the network mask of this cluster. Returns"
		"a CIDR value i, 0<=i<=32. Handles only IPv4 addresses."

		mask = 32
		Net = string.split(net, ".")
		for i in Net:
			for j in range(0,8):
				if int(i) & 2**j:
					break
				mask -= 1

		return mask


	def getSubnets(self):
		list = []

		network = self.getNetwork()
		netmask = self.getNetmask()

		w = string.split(network, '.')
		work = []
		for i in w:
			work.append(int(i))

		for i in range(0,4):
			if netmask < 8:
				break
			else:
				netmask -= 8

		octet_index = i
		octet_value = work[i]

		if netmask == 0:
			#
			# no subnetting
			#
			subnet = []

			for j in range(0, octet_index):
				subnet.append('%d' % (work[j]))

			list = [ subnet ]
		else:
			for i in range(0, 2**(8-netmask)):
				work[octet_index] = octet_value + i
				if work[octet_index] > 254:
					break

				subnet = []
				for j in range(0, octet_index+1):
					subnet.append('%d' % (work[j]))

				if list == []:
					list = [ subnet ]
				else:
					list.append(subnet)

		return list


	def run(self, params, args):
		self.runPlugins()
		os.system('/sbin/service named reload > /dev/null 2>&1')
