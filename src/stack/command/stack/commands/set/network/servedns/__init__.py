#@PYTHON@

# $Id$

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

# $Log$
# Revision 1.2  2010/09/07 23:53:02  bruno
# star power for gb
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

import stack.commands

class Command(stack.commands.NetworkArgumentProcessor,
	stack.commands.set.command):
	"""
	Sets/Unsets the capability for serving DNS
	for a given subnet
	<arg name='network' type='string'>
	Name of the Network
	</arg>
	<arg name='servedns' type='bool'>
	True/False
	</arg>
	<param name='servedns' type='bool'>
	True/False
	</param>
	
	"""
	def run(self, params, args):
		(args,servedns) = self.fillPositionalArgs(('servedns',))
		if len(args) < 1:
			self.abort('must supply network name')

		servedns = self.str2bool(servedns)
		for network in self.getNetworkNames(args):
			self.db.execute('update subnets set '	+\
				'servedns=%s ' % servedns	+\
				'where name="%s"' % network)
