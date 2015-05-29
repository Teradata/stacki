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
# Revision 1.20  2010/09/15 18:45:23  bruno
# don't yak if an attribute doesn't have a value. and if an attribute doesn't
# have a value, then don't dump it.
#
# Revision 1.19  2010/09/07 23:52:52  bruno
# star power for gb
#
# Revision 1.18  2009/06/19 23:11:20  mjk
# one more time with feeling
# quote {} and [] also
#
# Revision 1.17  2009/06/19 22:44:30  mjk
# remove dbg stuff
#
# Revision 1.16  2009/06/19 22:43:43  mjk
# forgot about wildcards
#
# Revision 1.15  2009/06/19 21:07:26  mjk
# - added dumpHostname to dump commands (use localhost for frontend)
# - added add commands for attrs
# - dump uses add for attr (does not overwrite installer set attrs)A
# - do not dump public or private interfaces for the frontend
# - do not dump os/arch host attributes
# - fix various self.about() -> self.abort()
#
# Revision 1.14  2009/05/01 19:06:56  mjk
# chimi con queso
#
# Revision 1.13  2009/04/03 22:47:57  mjk
# quote dump lines for the bash shell (bruno's magic from database-data.xml)
#
# Revision 1.12  2009/02/10 20:11:20  mjk
# os attr stuff for anoop
#
# Revision 1.11  2008/10/18 00:55:49  mjk
# copyright 5.1
#
# Revision 1.10  2008/03/06 23:41:36  mjk
# copyright storm on
#
# Revision 1.9  2007/07/04 01:47:37  mjk
# embrace the anger
#
# Revision 1.8  2007/07/02 17:31:06  bruno
# cleanup dump commands
#
# Revision 1.7  2007/06/23 03:54:52  mjk
# - first pass at consistency
# - still needs some docstrings
# - argument processors take SQL wildcards
# - add cannot run twice (must use set)
# - dump does sets not just adds
#
# Revision 1.6  2007/06/19 16:42:41  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.5  2007/06/11 19:26:58  mjk
# - apache counts as root
# - alphabetized some help flags
# - rocks dump error on arguments
#
# Revision 1.4  2007/06/08 03:26:24  mjk
# - plugins call self.owner.addText()
# - non-existant bug was real, fix plugin graph stuff
# - add set host cpus|membership|rack|rank
# - add list host (not /etc/hosts, rather the nodes table)
# - fix --- padding for only None fields not 0 fields
# - list host interfaces is cool works for incomplete hosts
#
# Revision 1.3  2007/06/07 21:23:04  mjk
# - command derive from verb.command class
# - default is MustBeRoot
# - list.command / dump.command set MustBeRoot = 0
# - removed plugin non-bugfix
#
# Revision 1.2  2007/06/07 16:43:02  mjk
# - moved host(s) argument processing into a top level class
# - list/dump/set host commands now use this
#
# Revision 1.1  2007/06/07 16:19:10  mjk
# - add "rocks add host"
# - add "rocks dump host"
# - add "rocks dump host interface"
# - remove "rocks add host new"
# - add mysql db init script to foundation-mysql
# - more flexible hostname lookup for the command line
#

import string
import stack.commands

class command(stack.commands.Command):
	MustBeRoot = 0

	safe_chars = [
		'@', '%', '^', '-', '_', '=', '+', 
		':', 
		',', '.', '/'
		]
		
	def quote(self, string):
		s = ''

		if string != None:
			for c in string:
				if c.isalnum() or c in self.safe_chars:
					s += c
				else:
					s += '\\%s' % c
		return s

	def dump(self, line):
		self.addText('echo "Running /opt/stack/bin/stack %s"\n' % line)
		self.addText('/opt/stack/bin/stack %s\n' % line)

	
class Command(command):
	"""
	The top level dump command is used to recursively call all the
	dump commands in the correct order.  This is used to create the 
	restore roll.

	<example cmd='dump'>
	Recursively call all dump commands.
	</example>
	"""
	
	def run(self, params, args):
		if len(args):
			self.abort('command does not take arguments')
		self.addText("#!/bin/bash\n\n")
		self.runPlugins()
		self.dump("sync config")
		self.dump("sync host config")

