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
# Revision 1.15  2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.14  2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.13  2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.12  2008/05/22 21:02:07  bruno
# rocks-dist is dead!
#
# moved default location of distro from /export/home/install to
# /export/stack/install
#
# Revision 1.11  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.10  2007/06/23 04:03:24  mjk
# mars hill copyright
#
# Revision 1.9  2006/09/11 22:47:23  mjk
# monkey face copyright
#
# Revision 1.8  2006/08/10 00:09:41  mjk
# 4.2 copyright
#
# Revision 1.7  2006/01/16 06:49:00  mjk
# fix python path for source built foundation python
#
# Revision 1.6  2005/10/12 18:08:42  mjk
# final copyright for 4.1
#
# Revision 1.5  2005/09/16 01:02:21  mjk
# updated copyright
#
# Revision 1.4  2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.3  2005/05/24 21:29:34  fds
# --product and --release are now dead.
#
# Revision 1.2  2005/05/24 21:21:57  mjk
# update copyright, release is not any closer
#
# Revision 1.1  2005/03/01 00:22:08  mjk
# moved to base roll
#
# Revision 1.14  2005/02/02 00:14:11  mjk
# remove --with-roll flag
#
# Revision 1.13  2004/10/18 23:24:12  fds
# More than rocks-dist parses rocks-distrc
#
# Revision 1.12  2004/09/07 23:25:29  fds
# Allow rcbase specification in parseArgs()
#
# Revision 1.11  2004/07/27 17:51:46  fds
# Knows about lan/wan dist types.
#
# Revision 1.10  2004/03/25 03:15:48  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.9  2004/03/03 19:31:57  fds
# Push ugly stuff into dist, tools are cleaner.
#
# Revision 1.8  2004/01/26 21:27:43  fds
# For WAN Kickstart
#
# Revision 1.7  2003/10/23 19:00:49  fds
# Typo
#
# Revision 1.6  2003/10/23 18:43:40  fds
# Added applyRPM convenience function. Used by
# several derived classes.
#
# Revision 1.5  2003/10/17 23:46:31  mjk
# Where is Yamhill
#
# Revision 1.4  2003/10/16 20:06:37  fds
# Fixed some architecture issues.
#
# Revision 1.3  2003/10/02 20:04:00  fds
# Setting arch type for self.distro in kickstart.Application. Added
# DistRPMList exception to getRPM so we can choose the correct kernel
# in dist.py. Small changes to app.py.
#
# Revision 1.2  2003/09/28 22:11:34  fds
# Understands path tags in rc file.
#
# Revision 1.1  2003/09/28 19:43:30  fds
# A rocks Application that knows certain things
# about the local distribution.
#
#

import os
import sys
import stack.sql
import stack.dist
from stack.dist import DistError


class Application(stack.sql.Application):
	"""A derivative of a rocks SQL application that knows certain things
	about the local Linux distribution. Used by kickstart.cgi, rollRPMS, 
	prep-initrd, and other tools.
	
	Responds to rocks-distrc resource control files."""
	

	def __init__(self, argv=None):
		stack.sql.Application.__init__(self, argv)
		self.rcfileHandler = RCFileHandler

		# Default to our native architecture.
		self.arch = self.getArch()

		# We use the simple base dist class. Rocks-dist requires
		# the more full-featured Distribution version. We do not
		# directly inherit from stack.dist to keep namespace clean.
		self.dist = stack.dist.Base()

		self.dist.setArch(self.arch)
		
		self.paths = {}

		self.rpmdb = os.path.join(os.getcwd(), 'rpmdb', 
			'var', 'lib', 'rpm')
		
		# Recognize distro flags for stack.dist module.
		self.getopt.s.extend(['a:', 'p:', 'l:', 'd:'])
		self.getopt.l.extend([('arch=', 'arch'),
			('product=', 'product'),
			('release=', 'release'),		
			('lang=', 'language')])


	def parseArgs(self, rcbase=None):

		# Soak in the options from the rocks-distrc file so
		# we know the path of our local distribution..

		self.parseRC('default')

		stack.sql.Application.parseArgs(self, rcbase)
		
	
	def parseArg(self, c):
		if stack.sql.Application.parseArg(self, c):
			return 1
		# Handling for distribution We include local attrs arch 
		# and lang for convenience.
		elif c[0] in ('-a', '--arch'):
			self.arch = c[1]
			self.dist.setArch(self.arch)
		elif c[0] == '--product':
			pass
		elif c[0] in ('--release',):
			pass
		elif c[0] in ('-l', '--lang'):
			self.lang = c[1]
		else:
			return 0
		return 1
		
		
	def readDist(self):
		"""Read in the RPM tree from our local distribution."""
		
		dist = self.dist.getDist()
		self.dist.setDist(dist)
		
		if not os.path.isdir(self.dist.getHomePath()):
			raise DistError, "Cannot find distribution %s" \
				% self.dist.getHomePath()
			
		if not self.dist.isBuilt():
			self.dist.build()
		

	def applyRPM(self, rpm):
		"""Installs an RPM package locally, in the current directory.
		A convenience function, which echoes logic in build.py.
		
		DEPRICATED: use rpm.apply() method instead."""
			
		if not rpm:
			raise DistError, "Couldn't find one of your rpms"

		if not os.path.exists(self.rpmdb):
			os.makedirs(self.rpmdb)			

		print "Applying:", rpm.getFullName()

		cmd = 'rpm -i --force --nodeps --badreloc --noscripts ' + \
			'--relocate /=%s/%s' % (os.getcwd(), rpm.getBaseName())
		cmd = cmd + ' --dbpath %s %s' % \
			(self.rpmdb, rpm.getFullName())

		rv = os.system(cmd)
		if rv == 256:
			raise DistError, "Could not apply one of your rpms"
		


class RCFileHandler(stack.app.RCFileHandler):
	
	def __init__(self, application):
		stack.app.RCFileHandler.__init__(self, application)

	def startElement_path(self, name, attrs):
		"""Parse the path tags. Since we only deal with built
		distros, we dont care about the 'local' pathname."""

		pathname = attrs.get('name')
		path = attrs.get('value')

		self.app.paths[pathname] = path

		if pathname == 'root':
			self.app.dist.setRoot(path)
		elif pathname == 'dist':
			self.app.dist.setDist(path)

