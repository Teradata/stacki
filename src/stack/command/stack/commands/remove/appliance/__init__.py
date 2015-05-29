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
# Revision 1.13  2010/09/07 23:52:57  bruno
# star power for gb
#
# Revision 1.12  2009/05/01 19:06:59  mjk
# chimi con queso
#
# Revision 1.11  2009/03/13 22:19:55  mjk
# - route commands done
# - cleanup of stack.host plugins
#
# Revision 1.10  2008/12/20 01:06:15  mjk
# - added appliance_attributes
# - attributes => node_attributes
# - rocks set,list,remove appliance attr
# - eval shell for conds has a special local dictionary that allows
#   unresolved variables (attributes) to evaluate to None
# - need to add this to solaris
# - need to move UserDict stuff into pylib and remove cut/paste code
# - need a drink
#
# Revision 1.9  2008/10/18 00:55:55  mjk
# copyright 5.1
#
# Revision 1.8  2008/03/06 23:41:38  mjk
# copyright storm on
#
# Revision 1.7  2007/07/04 01:47:39  mjk
# embrace the anger
#
# Revision 1.6  2007/06/26 20:21:15  bruno
# touch ups
#
# added 'fillParameters' -- now, every command will have fillParameters,
# fillPositionalArgs or neither.
#
# Revision 1.5  2007/06/19 16:42:42  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.4  2007/06/05 22:28:11  mjk
# require root for all remove commands
#
# Revision 1.3  2007/05/31 19:35:43  bruno
# first pass at getting all the 'help' consistent on all the rocks commands
#
# Revision 1.2  2007/05/10 20:37:02  mjk
# - massive rocks-command changes
# -- list host is standardized
# -- usage simpler
# -- help is the docstring
# -- host groups and select statements
# - added viz commands
#
# Revision 1.1  2007/04/12 19:48:05  bruno
# added command line: 'rocks add/list/remove appliance'
#
# updated base, hpc, pvfs2 and viz rolls to use new command line.
#
#


import stack.commands

class command(stack.commands.ApplianceArgumentProcessor,
	stack.commands.remove.command):
	pass

class Command(command):
	"""
	Remove an appliance definition from the system. This can be
	called with just the appliance or it can be further
	qualified by supplying the root XML node name and/or the
	graph XML file name.

	<arg type='string' name='name'>
	The name of the appliance.
	</arg>
	
	<example cmd='remove appliance compute'>
	Removes the compute appliance from the database.
	</example>
	"""

	def run(self, params, args):
		if len(args) < 1:
			self.abort('must supply at least one appliance')

		appliances = self.getApplianceNames(args)

		#
		# don't remove the default appliance
		#
		if 'backend' in appliances:
			self.abort('cannot remove default appliance')

		#
		# check if the appliance is associated with any hosts
		#
		for appliance in appliances:
			for row in self.call('list.host'):
				if row['appliance'] == appliance:
					self.abort('cannot remove appliance "%s"\nbecause host "%s" is assigned to this appliance' % (appliance, row['host']))

		#
		# good to go
		#
		for appliance in appliances:
			self.runPlugins(appliance)
