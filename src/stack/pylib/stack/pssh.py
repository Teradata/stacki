#! /opt/stack/bin/python
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
# Revision 1.18  2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.17  2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.16  2009/03/23 23:03:57  bruno
# can build frontends and computes
#
# Revision 1.15  2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.14  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.13  2007/06/23 04:03:24  mjk
# mars hill copyright
#
# Revision 1.12  2007/05/30 20:43:15  anoop
# *** empty log message ***
#
# Revision 1.11  2006/09/11 22:47:23  mjk
# monkey face copyright
#
# Revision 1.10  2006/08/10 00:09:41  mjk
# 4.2 copyright
#
# Revision 1.9  2006/01/16 06:49:00  mjk
# fix python path for source built foundation python
#
# Revision 1.8  2005/10/12 18:08:42  mjk
# final copyright for 4.1
#
# Revision 1.7  2005/10/06 18:49:30  mjk
# removed mpd
#
# Revision 1.6  2005/09/16 01:02:21  mjk
# updated copyright
#
# Revision 1.5  2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.4  2005/05/25 00:23:38  fds
# Using networks name rather than nodes name. Fixed mpd path.
#
# Revision 1.3  2005/05/24 21:21:57  mjk
# update copyright, release is not any closer
#
# Revision 1.2  2005/05/23 23:59:24  fds
# Frontend Restore
#
# Revision 1.1  2005/03/01 00:22:08  mjk
# moved to base roll
#
# Revision 1.22  2004/03/25 03:15:48  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.21  2004/03/16 18:24:34  fds
# Tweaks
#
# Revision 1.20  2004/03/16 18:21:05  fds
# Added support for reading list of hosts from an SGE pe-hostfile.
#
# Revision 1.19  2004/03/04 19:26:01  bruno
# look at nodes in ascending order
#
# Revision 1.18  2004/03/04 19:25:04  bruno
# IP address is no longer in nodes table
#
# Revision 1.17  2003/11/17 02:12:26  fds
# Listing nodes sucks for big jobs. Make it an option.
#
# Revision 1.16  2003/10/29 19:16:25  fds
# Using full mpd-mpirun path where necessary.
#
# Revision 1.15  2003/09/22 19:22:20  fds
# Added Tims idea for ssh background in cluster-fork.
#
# Revision 1.14  2003/09/16 21:07:19  fds
# Changes from Gouichi Iisaka (HP Japan)
#
# Revision 1.13  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.12  2003/08/05 23:46:54  fds
# Encoder class name change.
#
# Revision 1.11  2003/06/05 03:04:21  fds
# I realized that order in MPD nodelist has no
# bearing on output labels.
#
# Revision 1.10  2003/06/04 19:55:34  fds
# Better reporting, with an eye on screen-scraping.
#
# Revision 1.9  2003/05/30 00:29:24  fds
# Fixes from onyx
#
# Revision 1.8  2003/05/29 23:47:21  fds
# First draft of adding mpd backend.
#
# Revision 1.7  2003/05/22 16:39:28  mjk
# copyright
#
# Revision 1.6  2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.5  2003/02/06 00:00:05  bruno
# added -w1 flag -- thanks to Jessen Yu
#
# Revision 1.4  2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.3  2002/02/21 21:33:28  bruno
# added new copyright
#
# Revision 1.2  2001/10/25 21:41:44  bruno
# changes for new rocks sql schema
#
# Revision 1.1  2001/06/27 22:32:17  mjk
# - Added pssh.py module
# - Application now work when the HOME env var is not set
#

from __future__ import print_function
import os
import sys
import string
import getopt
import types
import stack.util
import stack.sql
import gmon.encoder


class ClusterFork(stack.sql.Application):

	def __init__(self, argv):
		stack.sql.Application.__init__(self, argv)

		self.query = ("select networks.name from " 
			+ "nodes,networks,memberships,subnets " 
			+ "where networks.node=nodes.id and "
			+ "nodes.membership=memberships.id and " 
			+ "memberships.compute='yes' and " 
			+ "subnets.name='private' and "
			+ "networks.subnet=subnets.id " 
			+ "order by nodes.rack,nodes.rank")
		self.nodes = []

		self.bg = 0
		self.verbose = 0

		# The node list encoder/decoder.
		self.e = gmon.encoder.Encoder()

		self.getopt.s.extend( [('q:', 'sql-expr'),'m',('n:','nodes')] )
		self.getopt.l.extend( [('query=', 'sql-expr'),
			('bg', 'Start SSH jobs in the background'),
			('verbose'),
			('nodes=', 'encoded node list'),
			('pe-hostfile=', 'sge machinefile') ] )


	def usageTail(self):
		return ' command'


	def parseArg(self, c):
		if stack.sql.Application.parseArg(self, c):
			return 1
		elif c[0] in ('-q', '--query'):
			self.query = c[1]
		elif c[0] in ('-n', '--nodes'):
			self.nodes = c[1]
		elif c[0] == '--pe-hostfile':
			nodes = []
			try:
				f = open(c[1],'r')
				for line in f.readlines():
					fields = line.split()
					# Node name is first
					nodes.append(fields[0])
				f.close()
				self.nodes = string.join(nodes)
			except:
				sys.stderr.write("Cannot read hostfile %s\n" 
					% c[1])
				sys.exit(1)
					
		elif c[0] in ('-v', '--verbose'):
			self.verbose = 1
		elif c[0] == '--bg':
			self.bg = 1
		else:
			return 0
		return 1


	def run(self, command=None):

		if self.nodes:
			nodelist = string.split(self.e.decode(self.nodes), " ")
		else:
			self.connect()
			self.execute(self.query)
			nodelist = []
			for host, in self.cursor.fetchall():
				nodelist.append(host)

		# If no command was supplied just use whatever was
		# left over on the argument list. 

		if not command:
			command = string.join(self.getArgs())
			if not command:
				self.help()
				sys.exit(0)

		sshflags = ""
			
		for hostname in nodelist:
			sys.stdout.write("%s: " % hostname)
			sys.stdout.flush()

			if os.system('ping -c1 -w1 %s > /dev/null 2>&1' % \
					(hostname)) == 0:
				print("")
					
				if self.bg:
					sshflags = "-f"

				os.system("ssh %s %s \"%s\"" % \
					(sshflags, hostname, command))
			else:
				print("down")

		print("")

