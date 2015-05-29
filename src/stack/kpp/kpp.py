#! @PYTHON@
#
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
# Revision 1.16  2010/09/07 23:53:07  bruno
# star power for gb
#
# Revision 1.15  2009/05/01 19:07:07  mjk
# chimi con queso
#
# Revision 1.14  2008/10/18 00:56:01  mjk
# copyright 5.1
#
# Revision 1.13  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.12  2007/06/23 04:03:23  mjk
# mars hill copyright
#
# Revision 1.11  2007/02/09 00:50:30  mjk
# more <copy> changes
#
# Revision 1.10  2007/01/10 18:39:57  mjk
# ignore unreadable <copy> files
#
# Revision 1.9  2007/01/10 17:37:50  mjk
# fix quoting
#
# Revision 1.8  2007/01/10 15:49:33  mjk
# added <copy> tag
#
# Revision 1.7  2006/09/11 22:47:20  mjk
# monkey face copyright
#
# Revision 1.6  2006/08/17 17:17:15  bruno
# removed the building and reading of the site-private.xml file.
#
# this fixes the problem of the parse error that occured when a " was in
# pure root password.
#
# a side-effect is that the variable Kickstart_PureRootPassword no longer
# exists. post sections that need a password, should pick from one of the
# encrypted Kickstart_*Password keys.
#
# Revision 1.5  2006/08/10 00:09:38  mjk
# 4.2 copyright
#
# Revision 1.4  2006/07/13 19:19:55  anoop
# Changed graph directions.
#
# Revision 1.3  2006/06/20 17:19:35  bruno
# add rocks version and release info to kpp
#
# Revision 1.2  2006/01/18 23:56:02  mjk
# fixed python path for eval tags
#
# Revision 1.1  2005/12/31 06:51:00  mjk
# move kpp into own package
#
# Revision 1.17  2005/10/12 18:08:39  mjk
# final copyright for 4.1
#
# Revision 1.16  2005/10/03 23:35:54  mjk
# pre-cook loader required tags
#
# Revision 1.15  2005/09/29 22:59:12  mjk
# always do 2nd pass, it only take .3 seconds
#
# Revision 1.14  2005/09/29 21:58:24  mjk
# python strings are slow
#
# Revision 1.13  2005/09/16 01:02:19  mjk
# updated copyright
#
# Revision 1.12  2005/07/20 23:13:04  mjk
# more foundation changes
#
# Revision 1.11  2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.10  2005/05/24 21:21:54  mjk
# update copyright, release is not any closer
#
# Revision 1.9  2005/05/24 16:49:09  mjk
# kickstart works again
#
# Revision 1.8  2005/05/23 23:59:23  fds
# Frontend Restore
#
# Revision 1.7  2005/03/16 04:43:16  fds
# Unquote site.xml vars for the post environment.
#
# Revision 1.6  2005/03/04 14:28:37  bruno
# removed umlat from log entry -- stops python warning regarding not
# specifying the encoding of kpp
#
# Revision 1.5  2005/03/04 02:21:15  mjk
# allow - inside roll name
#
# Revision 1.4  2005/03/02 20:30:51  mjk
# *** empty log message ***
#
# Revision 1.3  2005/03/01 19:24:39  mjk
# typo
#
# Revision 1.2  2005/03/01 18:21:32  mjk
# support for public/private nodes
#
# Revision 1.1  2005/03/01 02:02:48  mjk
# moved from core to base
#
# Revision 1.105  2005/02/17 22:15:54  mjk
# im a putz
#
# Revision 1.104  2005/02/16 00:07:30  mjk
# added Node_Root VAR
#
# Revision 1.103  2005/02/15 22:21:23  mjk
# Two passes are now used on all nodes files, the insures any generated
# code from EVAL tags gets the roll/file attributes.  We might want to
# extend this in the future to recurse, which would allow EVAL tags to
# create new EVAL tags.  Cool but we don't need it today.
#
# Revision 1.102  2005/02/01 23:58:54  mjk
# ignore roll attrs -- even though we just nuked them
#
# Revision 1.101  2005/02/01 23:08:24  mjk
# - minor cleanup
# - adds file,roll attrs to all output tags
# - eval / include do not do this (yet)
#
# Revision 1.100  2004/08/26 23:12:34  fds
# Passing client IP for shepherd.
#
# Revision 1.99  2004/07/16 18:16:07  mjk
# added sinclude tag to handle missing include files
#
# Revision 1.98  2004/07/16 11:44:26  bruno
# needed to XML escape var tags. the 'pure' root password is put into
# a var tag and if an XML escape character was present, it caused a parse
# error.
#
# this is part of the fix to bug 11.
#
# Revision 1.97  2004/06/30 22:50:08  fds
# New form. Kickstart.cgi is put in /home/install/sbin now, for various
# security-related reasons. kcgi knows about 'wan' and 'lan' distros, and
# has a new --dist flag.
#
# Revision 1.96  2004/06/14 23:21:03  fds
# Bugfix. Order tags with head and tail as attributes now work as expected.
#
# Revision 1.95  2004/04/28 17:35:53  bruno
# support for variabled-sized partitions root and swap partitions
#
# Revision 1.94  2004/04/22 14:55:39  mjk
# whitespace matters
#
# Revision 1.93  2004/04/22 14:21:55  mjk
# no invis dot edges by default
#
# Revision 1.92  2004/03/25 03:15:41  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.91  2004/03/11 21:41:38  fds
# Adopt mason's new rocks-dist capabilities. Allows a much cleaner WAN
# kickstart. Also added the ability to choose the distro name on central.
#
# Revision 1.90  2004/03/09 23:51:10  mjk
# fixed edge colors
#
# Revision 1.89  2004/02/12 22:57:48  fds
# Allow both landscape and portrait dot graph views.
#
# Revision 1.88  2004/02/09 21:56:21  fds
# We need to be a bit smarter here.
#
# Revision 1.87  2004/02/07 00:04:20  fds
# Adding roll attributes to package tags. Like what we did manually before.
#
# Revision 1.86  2004/02/05 00:56:47  mjk
# revert -- keep evals for roll subgraphs
#
# Revision 1.85  2004/02/05 00:40:20  mjk
# syntax error
#
# Revision 1.84  2004/02/05 00:37:17  mjk
# rollflag changed
#
# Revision 1.83  2004/02/04 17:39:38  bruno
# on what interface do you want to install?
#
# Revision 1.82  2004/02/03 23:28:11  mjk
# key is optional
#
# Revision 1.81  2004/02/03 22:59:20  mjk
# PDF looks great
#
# Revision 1.80  2004/02/03 21:16:09  mjk
# sort of like a roll
#
# Revision 1.79  2004/02/03 19:42:35  fds
# Allow user to specify dot graph bounding box.
#
# Revision 1.78  2004/02/03 00:01:00  mjk
# draw roll key
#
# Revision 1.77  2004/02/02 22:04:10  mjk
# edges and nodes can be colored now
#
# Revision 1.76  2004/02/02 21:43:31  mjk
# more dot changes
#
# Revision 1.75  2004/01/30 18:41:00  mjk
# more dot drawing
#
# Revision 1.74  2004/01/29 19:46:12  mjk
# fix --color flag
#
# Revision 1.73  2004/01/29 19:43:14  mjk
# dot graph on rolls
#
# Revision 1.72  2004/01/29 18:53:47  mjk
# dot graph for rolls
#
# Revision 1.71  2003/11/06 01:00:00  mjk
# use file tag for logging
#
# Revision 1.70  2003/11/06 00:45:41  mjk
# added logging on post sections
#
# Revision 1.69  2003/10/30 03:51:02  mjk
# Fixed single line edge tags.  This never worked, but should have.
#
# Revision 1.68  2003/10/23 17:36:45  fds
# Warns about unicode errors. Useful for catching names like Gotz Waschk.
#
# Revision 1.67  2003/10/16 21:01:27  mjk
# it works now
#
# Revision 1.66  2003/10/16 20:23:23  mjk
# - Removed default self.dist setting (doen't work for beta/taroon anyway)
# - Edges can now specify multiple arch,release as a comma seperated list
# - FrameworkEdges now use lists for arch and release
#
# Revision 1.65  2003/09/28 19:26:41  fds
# Need this error handling.
#
# Revision 1.64  2003/09/24 17:08:45  fds
# Bruno's changes for RH 9
#
# Revision 1.63  2003/09/16 18:08:35  fds
# Using KickstartError in trinity. Errors go to stderr.
#
# Revision 1.62  2003/08/26 22:44:20  mjk
# - File tag now takes "expr" attribute (command evaluation)
# - Conversion of old code to file tags
# - Added media-server (used to be server)
# - Killed replace-server on the hpc roll
# - Updated Server database membership (now a media-server)
# - Added Public field to the membership table
# - Insert-ethers only allows a subset of memberships (Public ones) to be
#   inserted.
# - Added getArch() to Application class
# - Kickstart trinity (kcgi,kpp,kgen) all updated self.arch initial value
#
# Revision 1.61  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.60  2003/08/14 17:38:38  mjk
# AW fixes
#
# Revision 1.59  2003/07/28 22:15:46  mjk
# Added support for python applets
#
# Revision 1.58  2003/07/11 23:55:51  bruno
# touch up on the rolls
#
# Revision 1.57  2003/07/07 22:35:27  bruno
# rocksversion was goofed
#
# Revision 1.56  2003/07/07 22:00:20  mjk
# fds +1/-1
#
# Revision 1.55  2003/07/07 21:53:00  mjk
# fds startElement fix remix
#
# Revision 1.54  2003/07/07 21:47:27  mjk
# fds startElement fix
#
# Revision 1.53  2003/07/07 20:16:52  bruno
# updates for rolls
#
# Revision 1.52  2003/06/27 22:27:10  fds
# Added basedir to enable kpp to run from any directory.
# Basedir should be /home/install/profiles/current or similar
#
# Revision 1.51  2003/06/27 14:19:24  bruno
# fixed directed edge direction on 'dot' graphs
#
# Revision 1.50  2003/05/22 16:36:35  mjk
# copyright
#
# Revision 1.49  2003/05/21 18:57:31  mjk
# grid integration checkpoint
#
# Revision 1.48  2003/04/29 18:38:47  mjk
# fixed HEAD node ordering
#
# Revision 1.47  2003/04/28 23:51:09  mjk
# who knows
#
# Revision 1.46  2003/04/25 23:16:09  mjk
# might as well gun it
#
# Revision 1.45  2003/04/24 23:22:07  mjk
# might fix everything
#
# Revision 1.44  2003/04/24 16:59:41  mjk
# - add order tags
# - edge and order tags can have children
# 	This just make the graph look nicer, no functional change
# - added include directory
# - moved install class code into include directory
# - dependecies enforced via topological sort
# - weight attributes are dead
# - long live order tags
# - the 'gen' attribute is currently ignored.  This will be used to support
#   other graph ordering requirements (e.g. testing, cfengine, ...)
#
# Revision 1.43  2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.42  2003/01/27 21:19:22  fds
# Rocks version and release now available to kickstart nodes as
# 'Info_RocksVersion' and 'Info_RocksRelease'.
#
# Revision 1.41  2003/01/09 18:32:54  mjk
# graph is a directory - it works now
#
# Revision 1.40  2002/12/22 16:20:08  bruno
# kpp now reads all files in the directory graphs/default/*
#
# Revision 1.39  2002/12/21 04:02:54  mjk
# *** empty log message ***
#
# Revision 1.38  2002/12/18 17:37:56  bruno
# bug fixes for 2.3.1
#
# Revision 1.37  2002/11/27 04:56:54  bruno
# fix: can now have user-settable NIS domains
#
# Revision 1.36  2002/11/13 22:20:00  mjk
# ia64 changes
#
# Revision 1.35  2002/10/28 19:50:40  mjk
# set hostname for frontend install
#
# Revision 1.34  2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.33  2002/10/18 19:49:02  mjk
# remove debug print
#
# Revision 1.32  2002/10/18 19:46:51  mjk
# fixed typos
#
# Revision 1.31  2002/10/18 19:43:51  mjk
# removed site- prefix from site specific nodes
#
# Revision 1.30  2002/10/18 19:33:57  mjk
# site-nodes
#
# Revision 1.29  2002/10/18 19:20:11  mjk
# Support for multiple mirrors
# Fixed insert-copyright for new CVS layout
#
# Revision 1.28  2002/10/16 14:27:51  bruno
# put try/except around the removal of /tmp/site-private.xml
#
# Revision 1.27  2002/10/15 23:32:19  fds
# Added private site.xml processing.
#
# Revision 1.26  2002/10/10 00:54:52  mjk
# Added close() to the database after using it
#
# Revision 1.25  2002/07/03 23:33:11  bruno
# 7.3 fixes
#
# Revision 1.24  2002/06/28 18:18:49  mjk
# checkpoint for XML vs SQL stuff
# might even work
#
# Revision 1.23  2002/06/17 19:50:02  bruno
# 7.3-isms
#
# Revision 1.22  2002/06/11 20:20:28  mjk
# Added support for release tag
#
# Revision 1.21  2002/04/22 20:32:50  mjk
# Added EOL DB2 Profile
#
# Revision 1.20  2002/02/25 19:08:43  mjk
# Negative package resolution for CDROM and CGI kickstart generation.  I
# lost a single line of python code in kpp that fixed this but it didn't
# get checked in.  Backed out of Greg's code and fixed my screw up.
#
# Revision 1.17  2002/01/18 23:27:58  bruno
# updates for 7.2
#
# Revision 1.16  2001/11/20 23:41:02  bruno
# small fixes for 2.1.1
#
# Revision 1.15  2001/11/09 23:50:53  mjk
# - Post release ia64 changes
#
# Revision 1.14  2001/10/24 00:15:47  mjk
# - Working on new kickstart form
#
# Revision 1.13  2001/10/19 22:11:36  mjk
# getting ready for php webform
#
# Revision 1.12  2001/09/21 18:36:53  mjk
# - Fixed multiple swapfiles
# - Added models CGI (and genmodel.py)
# - Kickstart CGI now accepts form data
# - Fixed turning off services (kudzu, et al)
#
# Revision 1.11  2001/09/18 17:39:52  mjk
# *** empty log message ***
#
# Revision 1.10  2001/09/14 23:33:50  mjk
# fixed for external hosts
#
# Revision 1.9  2001/09/14 23:20:42  mjk
# *** empty log message ***
#
# Revision 1.8  2001/09/14 23:08:49  mjk
# ia64 changes (still working on it)
#
# Revision 1.7  2001/09/14 21:45:42  mjk
# - Testing on ia32 compute nodes
# - A CGI kickstart takes 5 seconds
# - Working on ia64 compute nodes
#
# Revision 1.6  2001/09/10 18:57:54  mjk
# - Added --uml flag to kpp
# - RPMized
#
# Revision 1.5  2001/09/10 18:26:38  mjk
# *** empty log message ***
#
# Revision 1.4  2001/09/05 00:27:16  mjk
# main and packages section is correct for compute nodes
#
# Revision 1.3  2001/08/30 01:21:52  mjk
# merging kdot and kpp
#
# Revision 1.2  2001/08/28 02:51:30  mjk
# graph/nodes layout
#
# Revision 1.1  2001/08/21 01:52:39  mjk
# - <module> tag now prevent multiple inclusion
# - add dot support (ATT graph tool, just changed to GNU, we ship it now)
# - moved kickstart.cgi from rocks-dist RPM over here (called kcgi.py)
# - added <tree><node> tags
#

import os
import sys
import string
import xml
import popen2
import socket
import base64
import stack.sql
import stack.util
import stack.graph
from xml.sax import saxutils
from xml.sax import handler
from xml.sax import make_parser


class App(stack.sql.Application):

	def __init__(self, argv):
		stack.sql.Application.__init__(self, argv)
		self.usage_name		= 'Kickstart Pre-Processor'
		self.usage_version	= '@VERSION@'
		self.graph		= 'default'
		self.dist               = ''
		self.generator		= 'kgen'
		self.release            = '@REDHAT_RELEASE@'
		self.rocksversion	= '@ROCKS_VERSION@'
		self.rocksrelease	= '@RELEASE_NAME@'
		self.entities           = {}
		self.xmlNodes           = []
		self.client             = None
		self.clientIP           = ''
		self.doEval		= 1
		self.allowMissing	= 0
		self.drawEdges		= 1
		self.drawOrder		= 0
		self.drawKey		= 0
		self.drawInvisEdges	= 0
		self.drawLandscape	= 0
		self.roll		= ''
		self.drawSize		= '7.5,10'
		self.arch		= self.getArch()

		# Add application flags to inherited flags

		self.getopt.s.extend([
			('a:', 'architecture'),
			('c:', 'client'),
			('g:', 'graph')
			])
		self.getopt.l.extend([
			('allow-missing'),
			('arch=', 'architecture'),
			('client=', 'client'),
			('client-ip=', 'client addr'),
			('distribution=', 'distribution'),
			('draw-invis-edges'),
			('draw-order'),
			('draw-edges'),
			('draw-key'),
			('draw-all'),
			('draw-landscape','flip graph'),
			('draw-size=', 'dot graph size (H",W")'),
			('no-eval'),
			('generator=', 'gen'),
			('graph=', 'graph'),
			('roll=', 'subgraph for named pallet'),
			('uml')
			])

	def usageTail(self):
		return ' [file]'

	def pathElement(self, path, n):
		list = string.split(os.path.normpath(path), os.sep)
		if n < 0:
			list.reverse()
			n = abs(n)
		return list[n]

			
	def parseArg(self, c):
		if stack.sql.Application.parseArg(self, c):
			return 1
		if c[0] in ('-a', '--arch'):
			self.arch = c[1]
		elif c[0] == '--allow-missing':
			self.allowMissing = 1
		elif c[0] == '--draw-invis-edges':
			self.drawInvisEdges = 1
		elif c[0] == '--draw-order':
			self.drawOrder = 1
			self.drawEdges = 0
		elif c[0] == '--draw-edges':
			self.drawOrder = 0
			self.drawEdges = 1
		elif c[0] == '--draw-all':
			self.drawOrder = 1
			self.drawEdges = 1
			self.drawKey   = 1
		elif c[0] == '--draw-key':
			self.drawKey = 1
		elif c[0] == '--draw-size':
			self.drawSize = c[1]
		elif c[0] == '--draw-landscape':
			self.drawLandscape =1
		elif c[0] in ('-c', '--client'):
			self.client = c[1]
		elif c[0] in ('--client-ip',):
			self.clientIP = c[1]
		elif c[0] == '--distribution':
			self.dist    = c[1]
		elif c[0] == '--generator':
			self.generator = c[1]
		elif c[0] in ('-g', '--graph'):
			self.graph = c[1]
		elif c[0] == '--no-eval':
			self.doEval = 0
		elif c[0] == '--roll':
			self.roll = c[1]
		else:
			return 0
		return 1


	def getGroupName(self, membershipID):
		self.execute('select name from memberships where id=%s' \
			% membershipID)
		try:
			name, = self.fetchone()
		except:
			name = "Unknown"
		return name


	def getGroup(self, host):
		self.execute('select membership from nodes '
			'where site=0 and name="%s"' % host)
		try:
			group, = self.fetchone()
		except TypeError:
			group = 0
		return group

	def createEntitiesFromXML(self):
		sitefile = "site.xml"
		try:
			fin = open(os.path.join(os.sep, 'tmp', sitefile), 'r')
		except IOError:
			pass
			
		parser = make_parser()
		handler = SiteNodeHandler(self.entities)
		parser.setContentHandler(handler)
		parser.parse(fin)
		fin.close()

		hostname = self.entities.get('Kickstart_PrivateHostname')
		if hostname == None:
			self.entities['Node_Hostname' ] = ''
		else:
			self.entities['Node_Hostname' ] = hostname

		self.entities['Node_Distribution']  = self.dist
		self.entities['Node_DistName'] = self.dist.split('/')[0]
		self.entities['Node_Architecture']  = self.arch
		self.entities['Node_RedHatRelease'] = self.release

		self.entities['Info_RocksVersion']  = self.rocksversion
		self.entities['Info_RocksRelease'] = self.rocksrelease

	
	def createEntitiesFromDB(self):

		var = {}
		
		# Add some entities that come from command line
		# arguments.

		if self.client:
			var['Node_Hostname'] = self.client
		if self.clientIP:
			var['Node_Address'] = self.clientIP

		var['Node_Distribution']  = self.dist
		var['Node_DistName'] = self.dist.split('/')[0]
		var['Node_Architecture']  = self.arch
		var['Node_RedHatRelease'] = self.release
		var['Info_RocksVersion']  = self.rocksversion
		var['Info_RocksRelease'] = self.rocksrelease

		# Do not try to do this without a DB.
		m = self.getGroup(self.client)
		var['Node_Membership'] = self.getGroupName(m)

		# Create the var{} table of entities from the
		# app_globals table in the database.

		self.execute('select service,component,value '
			     'from app_globals where '
			     '(membership=0 or membership=%d) and site=0 '
			     'order by service,component,membership' %
			     self.getGroup(self.client))

		for service,component,value in self.fetchall():
			var[service + '_' + component] = value

		# Overwrite the default entities with the values from
		# the KCG_* variable.  This allow the php web form to
		# provide site specific state.

		for env in os.environ.keys():
			list = string.split(env, '_', 1)
			if len(list) == 2 and list[0] == 'Kickstart':
				var[env] = os.environ[env]

		self.entities = var


	def readDotGraphStyles(self):
		p   = make_parser()
		h   = RollHandler()
		map = {}
		
		for file in os.listdir('.'):
			tokens = os.path.splitext(file)
			if len(tokens) != 2:
				continue
			name = tokens[0]
			ext  = tokens[1]
			tokens = string.split(name, '-')
			if len(tokens) < 2:
				continue
			prefix = tokens[0]
			if prefix == 'roll' and \
			   ext == '.xml' and \
			   os.path.isfile(file):
				fin = open(file, 'r')
				p.setContentHandler(h)
				p.parse(fin)
				fin.close()
				r = h.getRollName()
				map[r] = stack.util.Struct()
				map[r].edgeColor = h.getEdgeColor()
				map[r].nodeColor = h.getNodeColor()
				map[r].nodeShape = h.getNodeShape()

		return map



	def createDotGraph(self, handler, styleMap):
		graph = handler.getMainGraph()
		print 'digraph %s {' % self.graph
		print '\tsize="%s";' % self.drawSize
		if self.drawLandscape:
			print '\trankdir=TB;'
		else:
			print '\trankdir=LR;'

		if self.drawKey:
			print '\tsubgraph clusterkey {'
			print '\t\tlabel="Rolls";'
			print '\t\tcolor=black;'
			for key in styleMap:
				a = 'style=filled '
				a = a + 'shape=%s '    % styleMap[key].nodeShape
				a = a + 'label="%s " ' % key
				a = a + 'fillcolor=%s' % styleMap[key].nodeColor
				print '\t\t"roll-%s" [%s];' % (key, a)
			print '\t}'

		for node in graph.getNodes():
			try:
				handler.parseNode(node, 0) # Skip <eval>
			except stack.util.KickstartNodeError:
				pass

			try:
				color = styleMap[node.getRoll()].nodeColor
			except:
				color = 'white'
			node.setFillColor(color)
			node.drawDot('\t')

		# Draw the edges with an optional architecture label

		if self.drawEdges:
			style = 'bold'
		else:
			style = 'invis'

		if self.drawEdges or self.drawInvisEdges:
			for e in graph.getEdges():
				try:
					color = styleMap[e.getRoll()].edgeColor
				except:
					color = 'black'
				e.setColor(color)
				e.setStyle(style)
				e.drawDot('\t')

		# Now include the order edges
			
		if self.drawOrder:
			style = 'bold'
		else:
			style = 'invis'

		if self.drawOrder or self.drawInvisEdges:
			for e in handler.getOrderGraph().getEdges():
				try:
					color = styleMap[e.getRoll()].edgeColor
				except:
					color = 'black'
				e.setColor(color)
				e.setStyle(style)
				e.drawDot('\t')


		print '}'


	def run(self):

		try:
			if self.connect():
				self.createEntitiesFromDB()
			else:
				raise Exception
			self.close()
		except:
			self.createEntitiesFromXML()
		
		# Parse the XML graph files in the chosen directory

		parser  = make_parser()
		handler = GraphHandler(self.entities)

		graph_dir = os.path.join('graphs', self.graph)

		if not os.path.exists(graph_dir):
			raise stack.util.KickstartGraphError, \
				"cannot find graph dir '%s'" % graph_dir

		for file in os.listdir(graph_dir):
			root, ext = os.path.splitext(file)
			if ext == '.xml':
				path = os.path.join(graph_dir, file)
				if os.path.isfile(path):
					fin = open(path, 'r')
					parser.setContentHandler(handler)
					parser.parse(fin)
					fin.close()

		# Without a node argument just dump a DOT-style graph
		# to show the object hierarchy.  Otherwise, we need to
		# traverse the graph from the given root node and
		# create the monolithic XML file.
		
		if not self.args:	
			self.createDotGraph(handler, self.readDotGraphStyles())
		else:

			rootName = self.args[0]
			
			# Node_Root is the name of the root xml file in
			# this graph traversal.
			
			self.entities['Node_Root'] = rootName
			
			graph = handler.getMainGraph()
			if graph.hasNode(rootName):
				root = graph.getNode(rootName)
			else:
				raise stack.util.KickstartNodeError, \
					'node %s not in graph' % rootName
				
			nodes = FrameworkIterator(graph).run(root)
			deps  = OrderIterator(handler.getOrderGraph()).run()


			# Initialize the hash table for the framework
			# nodes, and filter out everyone not for our
			# architecture and release.
			
			nodesHash = {}
			for node,arch,release in nodes:
				nodesHash[node.name] = node
				if arch and not self.arch in arch:
					nodesHash[node.name] = None
				if release and not self.release in release:
					nodesHash[node.name] = None
			

			# Initialize the hash table for the dependency
			# nodes, and filter out everyone not for our
			# generator type (e.g. 'kgen').

			depsHash = {}
			for node,gen in deps:
				depsHash[node.name] = node
				if gen not in [ None, self.generator ]:
					depsHash[node.name] = None

			for dep,gen in deps:
				if not nodesHash.has_key(dep.name):
					depsHash[dep.name] = None

			for node,arch,release in nodes:
				if depsHash.has_key(node.name):
					nodesHash[node.name] = None

			list = []
			for dep,gen in deps:
				if dep.name == 'TAIL':
					for node,arch,release in nodes:
						list.append(nodesHash[node.
								      name])
				else:
					list.append(depsHash[dep.name])

			#
			# if there was not a 'TAIL' tag, then add the
			# the nodes to the list here
			#
			for node,arch,release in nodes:
				if nodesHash[node.name] not in list:
					list.append(nodesHash[node.name])

			# Iterate over the nodes and parse everyone we need
			# to parse.
			
			parsed = []
			kstext = ''
			for node in list:
				if not node:
					continue

				# When building rolls allowMissing=1 and
				# doEval=0.  This is setup by rollRPMS.py

				if self.allowMissing:
					try:
						handler.parseNode(node,
								  self.doEval)
					except stack.util.KickstartNodeError:
						pass
				else:
					handler.parseNode(node, self.doEval)
					parsed.append(node)
					kstext += node.getKSText()

			
			# Now print everyone out with the header kstext from
			# the previously parsed nodes

			print '<?xml version="1.0" standalone="no"?>'
			print '<kickstart>'
			print '<loader>'
			print saxutils.escape(kstext)
			print '%kgen'
			print '</loader>'

			for node in parsed:

				# If we are only expanding a roll subgraph
				# then do not ouput the XML for other nodes
				
				if self.roll and node.getRoll() != self.roll:
					continue
				
				try:
					print node.getXML()
				except Exception, msg:
					raise stack.util.KickstartNodeError, \
					      "in %s node: %s" \
					      % (node, msg)
			print '</kickstart>'


			

class RollHandler(handler.ContentHandler,
		  handler.DTDHandler,
		  handler.EntityResolver,
		  handler.ErrorHandler):

	def __init__(self):
		handler.ContentHandler.__init__(self)
		self.rollName  = ''
		self.edgeColor = None
		self.nodeColor = None
		self.nodeShape = 'ellipse'

	def getRollName(self):
		return self.rollName
	
	def getEdgeColor(self):
		return self.edgeColor

	def getNodeColor(self):
		return self.nodeColor

	def getNodeShape(self):
		return self.nodeShape
	
	# <roll>
	
	def startElement_roll(self, name, attrs):
		self.rollName = attrs.get('name')
		
	
	# <color>
	
	def startElement_color(self, name, attrs):
		if attrs.get('edge'):
			self.edgeColor = attrs.get('edge')
		if attrs.get('node'):
			self.nodeColor = attrs.get('node')


	def startElement(self, name, attrs):
		try:
			eval('self.startElement_%s(name, attrs)' % name)
		except AttributeError:
			pass

	def endElement(self, name):
		try:
			eval('self.endElement_%s(name)' % name)
		except AttributeError:
			pass


	
class GraphHandler(handler.ContentHandler,
		   handler.DTDHandler,
		   handler.EntityResolver,
		   handler.ErrorHandler):

	def __init__(self, entities):
		handler.ContentHandler.__init__(self)
		self.graph			= stack.util.Struct()
		self.graph.main			= stack.graph.Graph()
		self.graph.order		= stack.graph.Graph()
		self.attrs			= stack.util.Struct()
		self.attrs.main			= stack.util.Struct()
		self.attrs.main.default		= stack.util.Struct()
		self.attrs.order		= stack.util.Struct()
		self.attrs.order.default	= stack.util.Struct()
		self.entities			= entities
		self.roll			= ''
		self.text			= ''
		

	def getMainGraph(self):
		return self.graph.main

	def getOrderGraph(self):
		return self.graph.order

	def parseNode(self, node, eval=1):
		if node.name in [ 'HEAD', 'TAIL' ]:
			return
		
		nodesPath = [ os.path.join('.',  'nodes'),
			      os.path.join('..', 'nodes'),
			      os.path.join('.',  'site-nodes'),
			      os.path.join('..', 'site-nodes')
			      ]

		# Find the xml file for each node in the graph.  If we
		# can't find one just complain and abort.

		xml = [ None, None, None ] # rocks, extend, replace
		for dir in nodesPath:
			if not xml[0]:
				file = os.path.join(dir, '%s.xml' % node.name)
				if os.path.isfile(file):
					xml[0] = file
			if not xml[1]:
				file = os.path.join(dir, 'extend-%s.xml'\
						    % node.name)
				if os.path.isfile(file):
					xml[1] = file
			if not xml[2]:
				file = os.path.join(dir, 'replace-%s.xml'\
						    % node.name)
				if os.path.isfile(file):
					xml[2] = file

		if not (xml[0] or xml[2]):
			raise stack.util.KickstartNodeError, \
			      'cannot find node "%s"' % node.name

		xmlFiles = [ xml[0] ]
		if xml[1]:
			xmlFiles.append(xml[1])
		if xml[2]:
			xmlFiles = [ xml[2] ]

		for xmlFile in xmlFiles:
		
			# 1st Pass
			#	- Expand VAR tags
			#	- Expand EVAL tags
			#	- Expand INCLUDE/SINCLUDE tag
			#	- Logging for post sections
			
			fin = open(xmlFile, 'r')
			parser = make_parser()
			handler = Pass1NodeHandler(node, xmlFile, 
				self.entities, eval)
			parser.setContentHandler(handler)
			parser.parse(fin)
			fin.close()
			
			# 2nd Pass
			#	- Annotate all tags with ROLL attribute
			#	- Annotate all tags with FILE attribute
			#	- Strip off KICKSTART tags
			#
			# The second pass is required since EVAL tags can
			# create their own XML, instead of requiring the
			# user to annotate we do it for them.
			
			parser = make_parser()
			xml = handler.getXML()
			handler = Pass2NodeHandler(node)
			parser.setContentHandler(handler)
			parser.feed(xml)

			# Attach the final XML to the node object so we can find
			# it again.
			
			node.addXML(handler.getXML())
			node.addKSText(handler.getKSText())


	def addOrder(self):
		if self.graph.order.hasNode(self.attrs.order.head):
			head = self.graph.order.getNode(self.attrs.order.head)
		else:
			head = Node(self.attrs.order.head)

		if self.graph.order.hasNode(self.attrs.order.tail):
			tail = self.graph.order.getNode(self.attrs.order.tail)
		else:
			tail = Node(self.attrs.order.tail)

		e = OrderEdge(head, tail, self.attrs.order.gen)
		e.setRoll(self.roll)
		self.graph.order.addEdge(e)


	def addEdge(self):
		if self.graph.main.hasNode(self.attrs.main.parent):
			head = self.graph.main.getNode(self.attrs.main.parent)
		else:
			head = Node(self.attrs.main.parent)

		if self.graph.main.hasNode(self.attrs.main.child):
			tail = self.graph.main.getNode(self.attrs.main.child)
		else:
			tail = Node(self.attrs.main.child)

		e = FrameworkEdge(tail, head)
		e.setArchitecture(self.attrs.main.arch)
		e.setRelease(self.attrs.main.release)
		e.setRoll(self.roll)
		self.graph.main.addEdge(e)


	# <graph>

	def startElement_graph(self, name, attrs):
		if attrs.get('roll'):
			self.roll = attrs.get('roll')
		else:
			self.roll = 'base'

	# <head>

	def startElement_head(self, name, attrs):
		self.text		= ''
		self.attrs.order.gen	= self.attrs.order.default.gen
		
		if attrs.has_key('gen'):
			self.attrs.order.gen = attrs['gen']


	def endElement_head(self, name):
		self.attrs.order.head = self.text
		self.addOrder()
		self.attrs.order.head = None


	# <tail>

	def startElement_tail(self, name, attrs):
		self.text		= ''
		self.attrs.order.gen	= self.attrs.order.default.gen

		if attrs.has_key('gen'):
			self.attrs.order.gen = attrs['gen']

	def endElement_tail(self, name):
		self.attrs.order.tail = self.text
		self.addOrder()
		self.attrs.order.tail = None


	# <to>

	def startElement_to(self, name, attrs):	
		self.text		= ''
		self.attrs.main.arch	= self.attrs.main.default.arch
		self.attrs.main.release	= self.attrs.main.default.release

		if attrs.has_key('arch'):
			self.attrs.main.arch = attrs['arch']
		if attrs.has_key('release'):
			self.attrs.main.release = attrs['release']

	def endElement_to(self, name):
		self.attrs.main.parent = self.text
		self.addEdge()	
		self.attrs.main.parent = None
	

	# <from>

	def startElement_from(self, name, attrs):
		self.text		= ''
		self.attrs.main.arch	= self.attrs.main.default.arch
		self.attrs.main.release	= self.attrs.main.default.release
		
		if attrs.has_key('arch'):
			self.attrs.main.arch = attrs['arch']
		if attrs.has_key('release'):
			self.attrs.main.release = attrs['release']


	def endElement_from(self, name):
		self.attrs.main.child = self.text
		self.addEdge()
		self.attrs.main.child = None
		
	# <order>

	def startElement_order(self, name, attrs):
		if attrs.has_key('head'):
			self.attrs.order.head = attrs['head']
		else:
			self.attrs.order.head = None
		if attrs.has_key('tail'):
			self.attrs.order.tail = attrs['tail']
		else:
			self.attrs.order.tail = None
		if attrs.has_key('gen'):
			self.attrs.order.default.gen = attrs['gen']
		else:
			self.attrs.order.default.gen = None
		self.attrs.order.gen = self.attrs.order.default.gen
			
	def endElement_order(self, name):
		if self.attrs.order.head and self.attrs.order.tail:
			self.addOrder()



	# <edge>
	
	def startElement_edge(self, name, attrs):
		if attrs.has_key('arch'):
			self.attrs.main.default.arch = attrs['arch']
		else:
			self.attrs.main.default.arch = None
		if attrs.has_key('release'):
			self.attrs.main.default.release = attrs['release']
		else:
			self.attrs.main.default.release	= None
		if attrs.has_key('to'):
			self.attrs.main.parent = attrs['to']
		else:
			self.attrs.main.parent = None
		if attrs.has_key('from'):
			self.attrs.main.child = attrs['from']
		else:
			self.attrs.main.child = None

		self.attrs.main.arch	= self.attrs.main.default.arch
		self.attrs.main.release	= self.attrs.main.default.release


	def endElement_edge(self, name):
		if self.attrs.main.parent and self.attrs.main.child:
			self.addEdge()



	def startElement(self, name, attrs):
		try:
			func = getattr(self, "startElement_%s" % name)
		except AttributeError:
			return
		func(name, attrs)


	def endElement(self, name):
		try:
			func = getattr(self, "endElement_%s" % name)
		except AttributeError:
			return
		func(name)

		
	def endDocument(self):
		pass


	def characters(self, s):
		self.text = self.text + s





class SiteNodeHandler(handler.ContentHandler,
	handler.DTDHandler,
	handler.EntityResolver,
	handler.ErrorHandler):

	def __init__(self, entities):
		handler.ContentHandler.__init__(self)
		self.entities = entities
	
	# <var>
	
	def startElement_var(self, name, attrs):
		varName = attrs.get('name')
		varRef  = attrs.get('ref')
		varVal  = attrs.get('val')

		# Undo quoting from writeSiteVar()

		varName = varName.replace("\\'","'")

		if varVal:
			varVal = varVal.replace("\\'","'")
			self.entities[varName] = varVal
		elif varRef:
			if self.entities.has_key(varRef):
				self.entities[varName] = self.entities[varRef]
			else:
				self.entities[varName] = ''

	def startElement(self, name, attrs):
		try:
			eval('self.startElement_%s(name, attrs)' % name)
		except AttributeError:
			pass

	def endElement(self, name):
		try:
			eval('self.endElement_%s(name)' % name)
		except AttributeError:
			pass
		


class Pass1NodeHandler(handler.ContentHandler,
	handler.DTDHandler,
	handler.EntityResolver,
	handler.ErrorHandler):

	"""Sax Parser for the Kickstart Node files"""

	def __init__(self, node, filename, entities, eval=0):
		handler.ContentHandler.__init__(self)
		self.node	= node
		self.entities	= entities
		self.evalShell	= None
		self.evalText	= []
		self.copyData	= None
		self.doEval	= eval
		self.doCopy	= eval
		self.xml	= []
		self.filename	= filename
		self.stripText  = 0

	def startElement_description(self, name, attrs):
		self.stripText = 1

	def endElement_description(self, name):
		pass

	def startElement_changelog(self, name, attrs):
		self.stripText = 1

	def endElement_changelog(self, name):
		pass

	def startElement_copyright(self, name, attrs):
		self.stripText = 1

	def endElement_copyright(self, name):
		pass
	
	# <kickstart>
	
	def startElement_kickstart(self, name, attrs):
	
		# Setup the Node object to know what roll and what filename 
		# this XML came from.  We use this on the second pass to
		# annotated every XML tag with this information
		
		if attrs.get('roll'):
			self.node.setRoll(attrs.get('roll'))
		else:
			self.node.setRoll('unknown')
			

		# Rolls can define individual nodes to be "interface=public".
		# All this does is change the shape of the node on the
		# kickstart graph.  This helps define well know grafting
		# points inside the graph (for example, in the base roll).
 
		if attrs.get('interface'):
			self.node.setShape('box')
		else:
			self.node.setShape('ellipse')
 
			
		self.node.setFilename(self.filename)
		self.startElementDefault(name, attrs)
			
	
	# <include>

	def startElement_include(self, name, attrs):
		filename = attrs.get('file')
		if attrs.get('mode'):
			mode = attrs.get('mode')
		else:
			mode = 'quote'

		file = open(os.path.join('include', filename), 'r')
		for line in file.readlines():
			if mode == 'quote':
				self.xml.append(saxutils.escape(line))
			else:
				self.xml.append(line)
		file.close()

	def endElement_include(self, name):
		pass
	
	# <sinclude> - same as include but allows for missing files

	def startElement_sinclude(self, name, attrs):
		try:
			self.startElement_include(name, attrs)
		except IOError:
			return

	def endElement_sinclude(self, name):
		pass

	# <var>

	def startElement_var(self, name, attrs):
		varName = attrs.get('name')
		varRef  = attrs.get('ref')
		varVal  = attrs.get('val')

		if varVal:
			self.entities[varName] = varVal
		elif varRef:
			if self.entities.has_key(varRef):
				self.entities[varName] = self.entities[varRef]
			else:
				self.entities[varName] = ''
		elif varName:
			#
			# if the entity value is 'None', then we must set
			# it to the empty string. this is because the
			# 'escape' method throws an exception when it
			# tries to XML escape a None type.
			#
			x = self.entities.get(varName)
			if not x:
				x = ''
			
			self.xml.append(saxutils.escape(x))

	def endElement_var(self, name):
		pass

	# <copy>

	def startElement_copy(self, name, attrs):
		if not self.doCopy:
			return
		if attrs.get('src'):
			src = attrs.get('src')
		if attrs.get('dst'):
			dst = attrs.get('dst')
		else:
			dst = src
		tmpfile = '/tmp/kpp.base64'
		self.xml.append('<file name="%s"/>\n' % dst)
		self.xml.append('<file name="%s">\n' % tmpfile)
		try:
			file = open(src, 'r')
			data = base64.encodestring(file.read())
			file.close()
		except IOError:
			data = ''
		self.xml.append(data)
		self.xml.append('</file>\n')
		self.xml.append("cat %s | /opt/stack/bin/python -c '" % tmpfile)
		self.xml.append('\nimport base64\n')
		self.xml.append('import sys\n')
		self.xml.append("base64.decode(sys.stdin, sys.stdout)' > %s\n"
			 % (dst))
		self.xml.append('rm -rf /tmp/kpp.base64\n')
		self.xml.append('rm -rf /tmp/RCS/kpp.base64,v\n')

	def endElement_copy(self, name):
		pass

	# <eval>
	
	def startElement_eval(self, name, attrs):
		if not self.doEval:
			return
		if attrs.get('shell'):
			self.evalShell = attrs.get('shell')
		else:
			self.evalShell = 'sh'
		if attrs.get('mode'):
			self.evalMode = attrs.get('mode')
		else:
			self.evalMode = 'quote'

		# Special case for python: add the applets directory
		# to the python path.

		if self.evalShell == 'python':
			self.evalShell = os.path.join(os.sep,
				'opt', 'rocks', 'bin', 'python')
			self.evalText = ['import sys\nimport os\nsys.path.append(os.path.join("include", "applets"))\n']
			
		
	def endElement_eval(self, name):
		if not self.doEval:
			return
		for key in self.entities.keys():
			os.environ[key] = self.entities[key]
		r, w = popen2.popen2(self.evalShell)
		for line in self.evalText:
			w.write(line)
		w.close()
		for line in r.readlines():
			if self.evalMode == 'quote':
				self.xml.append(saxutils.escape(line))
			else:
				self.xml.append(line)
		self.evalText  = []
		self.evalShell = None


	# <post>

	def startElement_post(self, name, attrs):
		self.xml.append('\n'
			'<post>\n'
			'<file name="/root/install.log" mode="append">\n'
			'%s: begin post section\n'
			'</file>\n'
			'</post>\n'
			'\n' %
			self.node.getFilename())
		self.startElementDefault(name, attrs)

	def endElement_post(self, name):
		self.endElementDefault(name)
		self.xml.append('\n'
			'<post>\n'
			'<file name="/root/install.log" mode="append">\n'
			'%s: end post section\n'
			'</file>\n'
			'</post>\n'
			'\n' %
			self.node.getFilename())

	# <*>

	def startElementDefault(self, name, attrs):
		s = ''
		for attrName in attrs.getNames():
			if attrName not in [ 'roll', 'file' ]:
				attrValue = attrs.get(attrName)
				s += ' %s="%s"' % (attrName, attrValue)
		if not s:
			self.xml.append('<%s>' % name)
		else:
			self.xml.append('<%s %s>' % (name, s))
		
	def endElementDefault(self, name):
		self.xml.append('</%s>' % name)


		
	def startElement(self, name, attrs):
		try:
			func = getattr(self, "startElement_%s" % name)
		except AttributeError:
			self.startElementDefault(name, attrs)
			return
		func(name, attrs)


	def endElement(self, name):
		try:
			func = getattr(self, "endElement_%s" % name)
		except AttributeError:
			self.endElementDefault(name)
			return
		func(name)
		self.stripText = 0

	def characters(self, s):
		if self.stripText:
			return

		if self.evalShell:
			self.evalText.append(s)
		else:
			self.xml.append(saxutils.escape(s))
			
	def getXML(self):
		return string.join(self.xml, '')


class Pass2NodeHandler(handler.ContentHandler,
	handler.DTDHandler,
	handler.EntityResolver,
	handler.ErrorHandler):

	"""Sax Parser for XML before it is written to stdout.  All generated XML 
	is filtered through this to append the file and roll attributes to
	all tags.  The includes tags generated from eval and include
	sections."""
		

	def __init__(self, node):
		handler.ContentHandler.__init__(self)
		self.node = node
		self.xml = []
		self.kstags  = {}
		self.kskey = None
		self.kstext = []

	def startElement(self, name, attrs):
		self.kstext = []
		
		if name == 'kickstart':
			return

		if name in [ 'url', 'lang', 'keyboard', 'text', 'reboot' ]:
			self.kskey = name
		else:
			self.kskey = None
						
		s = ''
		for attrName in attrs.getNames():
			attrValue = attrs.get(attrName)
			s += ' %s="%s"' % (attrName, attrValue)
		if 'roll' not in attrs.getNames():
			s += ' roll="%s"' % self.node.getRoll()
		if 'file' not in attrs.getNames():
			s += ' file="%s"' % self.node.getFilename()
		self.xml.append('<%s%s>' % (name, s))
		
	def endElement(self, name):
		if name == 'kickstart':
			return

		if self.kskey:
			self.kstags[self.kskey] = string.join(self.kstext, '')
			
		self.xml.append('</%s>' % name)

	def characters(self, s):
		self.kstext.append(s)
		self.xml.append(saxutils.escape(s))
		
	def getKSText(self):
		text = ''
		for key, val in self.kstags.items():
			text += '%s %s\n' % (key, val)
		return text
		
	def getXML(self):
		return string.join(self.xml, '')

	
				
				
class Node(stack.graph.Node):

	def __init__(self, name):
		stack.graph.Node.__init__(self, name)
		self.color	= 'black'
		self.fillColor	= 'white'
		self.shape	= 'ellipse'
		self.roll	= ''
		self.filename	= ''
		self.xml	= []
		self.kstext	= []

	def setColor(self, color):
		self.color = color

	def setFilename(self, filename):
		self.filename = filename
	
	def setFillColor(self, color):
		self.fillColor = color
		
	def setShape(self, shape):
		self.shape = shape

	def setRoll(self, name):
		self.roll = name
	
	def addKSText(self, text):
		self.kstext.append(text)
			
	def addXML(self, xml):
		self.xml.append(xml)
		
	def getFilename(self):
		return self.filename
		
	def getRoll(self):
		return self.roll

	def getXML(self):
		return string.join(self.xml, '')

	def getKSText(self):
		return string.join(self.kstext, '')

	def drawDot(self, prefix=''):
		attrs = 'style=filled '
		attrs = attrs + 'shape=%s '     % self.shape
		attrs = attrs + 'label="%s" '   % self.name
		attrs = attrs + 'fillcolor=%s ' % self.fillColor
		attrs = attrs + 'color=%s'      % self.color
		print '%s"%s" [%s];' % (prefix, self.name, attrs)
		

class Edge(stack.graph.Edge):
	def __init__(self, a, b):
		stack.graph.Edge.__init__(self, a, b)
		self.roll	= ''
		self.color	= 'black'
		self.style	= ''

	def setStyle(self, style):
		self.style = style
		
	def setColor(self, color):
		self.color = color

	def setRoll(self, name):
		self.roll = name
		
	def getRoll(self):
		return self.roll

		

class FrameworkEdge(Edge):
	def __init__(self, a, b):
		Edge.__init__(self, a, b)
		self.arch    = None
		self.release = None

	def setArchitecture(self, arch):
		if arch:
			self.arch = []
			for e in string.split(arch, ','):
				self.arch.append(string.strip(e))

	def getArchitecture(self):
		return self.arch


	def setRelease(self, release):
		if release:
			self.release = []
			for e in string.split(release, ','):
				self.release.append(string.strip(e))


	def getRelease(self):
		return self.release


	def drawDot(self, prefix=''):
		attrs = ''
		attrs = attrs + 'style=%s ' % self.style
		attrs = attrs + 'color=%s ' % self.color
		attrs = attrs + 'arrowsize=1.5 '
		if self.arch:
			arch = string.join(self.arch, '\\n')
			attrs = attrs + 'label="%s"' % arch

		print '%s"%s" -> "%s" [%s];' % (prefix, self.parent.name,
						self.child.name,
						attrs)


class OrderEdge(Edge):
	def __init__(self, head, tail, gen=None):
		Edge.__init__(self, head, tail)
		self.gen = gen

	def getGenerator(self):
		return self.gen

	def drawDot(self, prefix=''):
		attrs = ''
		attrs = attrs + 'style=%s ' % self.style
		attrs = attrs + 'color=%s ' % self.color
		attrs = attrs + 'arrowhead=dot arrowsize=1.5'
		print '%s"%s" -> "%s" [%s];' % (prefix, self.parent.name,
						self.child.name,
						attrs)



class FrameworkIterator(stack.graph.GraphIterator):
	def __init__(self, graph):
		stack.graph.GraphIterator.__init__(self, graph)
		self.nodes = []

	def run(self, node):
		stack.graph.GraphIterator.run(self, node)
		return self.nodes
	
	def visitHandler(self, node, edge):
		stack.graph.GraphIterator.visitHandler(self, node, edge)
		if edge:
			arch    = edge.getArchitecture()
			release = edge.getRelease()
		else:
			arch    = None
			release = None
		self.nodes.append((node, arch, release))


class OrderIterator(stack.graph.GraphIterator):
	def __init__(self, graph):
		stack.graph.GraphIterator.__init__(self, graph)
		self.nodes = []
		self.mark  = {}

	def run(self):

		# First pass: Mark all nodes that have a path to HEAD.
		# We do this by reversing all edges in the graph, and
		# marking all nodes in HEAD's subtree.  Then for all
		# the unmarked nodes create an edge from HEAD to the
		# node.  This will force the HEAD node to be as close
		# as possible to the front of the topological order.

		self.nodes = []		# We don't really use these but we
		self.time  = 0		# might as well intialize them
		for node in self.graph.getNodes():
			self.mark[node] = 0
		self.graph.reverse()
		head = self.graph.getNode('HEAD')
		stack.graph.GraphIterator.run(self, head)
		self.graph.reverse()	# restore edge order

		for node in self.graph.getNodes():
			if not self.mark[node] and node.getInDegree() == 0:
				self.graph.addEdge(OrderEdge(head, node))

		
		# Second pass: Mask all nodes reachable from TAIL.
		# Then for all the unmarked nodes create an edge from
		# TAIL to the node.  This will force TAIL to be as
		# close as possible to the end of the topological
		# order.

		self.nodes = []		# We don't really use these but we
		self.time  = 0		# might as well intialize them
		for node in self.graph.getNodes():
			self.mark[node] = 0
		tail = self.graph.getNode('TAIL')
		stack.graph.GraphIterator.run(self, tail)

		for node in self.graph.getNodes():
			if not self.mark[node] and node.getOutDegree() == 0:
				self.graph.addEdge(OrderEdge(node, tail))
		

		# Third pass: Traverse the entire graph and compute
		# the finishing times for each node.  The reverse sort
		# of the finishing times produces the topological
		# ordering of the graph.  This ordered list of nodes
		# satisifies all of the dependency edges.
		
		self.nodes = []
		self.time  = 0
		stack.graph.GraphIterator.run(self)

		list = []
		self.nodes.sort()
		for rank, node, gen in self.nodes:
			list.append((node, gen))
		list.reverse()

		return list


	def visitHandler(self, node, edge):
		stack.graph.GraphIterator.visitHandler(self, node, edge)
		self.mark[node] = 1
		self.time = self.time + 1

	def finishHandler(self, node, edge):
		stack.graph.GraphIterator.finishHandler(self, node, edge)
		self.time = self.time + 1
		if edge:
			gen = edge.getGenerator()
		else:
			gen = None
		self.nodes.append((self.time, node, gen))

		
app = App(sys.argv)
app.parseArgs()
try:
	app.run()
except stack.util.KickstartError, msg:
	sys.stderr.write("kpp error - %s\n" % msg)
	sys.exit(-1)

