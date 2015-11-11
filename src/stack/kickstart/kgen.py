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
# Revision 1.21  2010/09/07 23:53:07  bruno
# star power for gb
#
# Revision 1.20  2009/05/01 19:07:07  mjk
# chimi con queso
#
# Revision 1.19  2009/04/27 18:03:33  bruno
# remove dead setRCS* and getRCS* functions
#
# Revision 1.18  2008/10/18 00:56:01  mjk
# copyright 5.1
#
# Revision 1.17  2008/03/06 23:41:43  mjk
# copyright storm on
#
# Revision 1.16  2007/12/13 02:53:40  bruno
# can now build a bootable kernel CD and build a physical frontend with V
# on RHEL 5 update 1
#
# Revision 1.15  2007/12/10 21:28:35  bruno
# the base roll now contains several elements from the HPC roll, thus
# making the HPC roll optional.
#
# this also includes changes to help build and configure VMs for V.
#
# Revision 1.14  2007/08/14 20:24:34  anoop
# Moved the generator class functions from kgen.py to pylib.
# This allows us to simplify kgen, and make the functions
# accessible to the command line as well.
#
# Revision 1.13  2007/06/23 04:03:23  mjk
# mars hill copyright
#
# Revision 1.12  2006/09/11 22:47:16  mjk
# monkey face copyright
#
# Revision 1.11  2006/08/10 00:09:37  mjk
# 4.2 copyright
#
# Revision 1.10  2006/01/27 22:29:43  bruno
# stable (mostly) after integration of new foundation and localization code
#
# Revision 1.9  2006/01/16 06:48:58  mjk
# fix python path for source built foundation python
#
# Revision 1.8  2005/10/12 18:08:39  mjk
# final copyright for 4.1
#
# Revision 1.7  2005/10/04 00:11:40  mjk
# fixed order debug message now that descriptions tags are stripped
#
# Revision 1.6  2005/09/16 01:02:19  mjk
# updated copyright
#
# Revision 1.5  2005/08/25 16:57:20  mjk
# set arch by default
#
# Revision 1.4  2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.3  2005/05/24 21:21:54  mjk
# update copyright, release is not any closer
#
# Revision 1.2  2005/03/12 00:01:52  bruno
# minor checkin
#
# Revision 1.1  2005/03/01 02:02:48  mjk
# moved from core to base
#
# Revision 1.69  2005/02/14 20:10:34  mjk
# fix arch check
#
# Revision 1.68  2005/02/11 23:38:16  mjk
# - blow up the bridge
# - kgen and kroll do actually work (but kroll is not complete)
# - file,roll attrs added to all tags by kpp
# - gen has generator,nodefilter base classes
# - replaced rcs ci/co code with new stuff
# - very close to adding rolls on the fly
#
# Revision 1.67  2004/12/11 00:26:43  fds
# Fixed bug that would cause touched files with perms attributes to fail (such as in shepherd.xml).
#
# Revision 1.66  2004/11/24 20:30:55  bruno
# this fixes the following problem:
#
# - someone creates a new appliance
# - in the node XML for the new appliance, they include custom partitioning info
# - when kickstart.cgi is run, it outputs:
#
# 	part <custom 1>
# 	part <custom 2>
# 	part <custom 3>
# 	.
# 	.
# 	.
# 	part
#
# the last 'part' tells the installer to add the default partitioning (this
# came from auto-partition.xml), thus, the new appliance gets the custom
# partitioning *and* the default partitioning.
#
# the fix: if custom partitioning is specified, then don't output 'part'. if
# custom partitioning is not specified, then do output 'part'.
#
# Revision 1.65  2004/09/18 15:09:34  bruno
# ok, i think i really got it now.
#
# backed out the change to kgen.py
#
# moved the 'disable' kernel package from node-thin to media-server
#
# and, make sure that a kickstarting host doesn't explictly call out the
# kernel or kernel-smp packages
#
# Revision 1.64  2004/09/18 14:30:15  bruno
# some tweaks to let anaconda decide which package to install (kernel or
# kernel-smp) because if we explictly set it (e.g., kernel-smp), then
# there is the case where the kernel-smp package is installed on an EM64T
# node and only the 'kernel' package should be on it.
#
# Revision 1.63  2004/08/27 18:21:06  bruno
# add a package to the "off" list when it is not in the "on" list.
#
# and, a package in the "on" list means it must not be in the "off" list.
#
# makes sense, yes?
#
# Revision 1.62  2004/04/27 17:18:59  fds
# I respectfully submit the following changes. It is less code, more inline with
# the strategies used in other parts of the kickstart generation, and has the
# same behavior as before.
#
# Revision 1.61  2004/04/27 04:38:48  bruno
# added ability to just print out 'pre' section.
#
# Revision 1.60  2004/03/25 03:15:41  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.59  2004/02/25 18:12:33  mjk
# strip ws from packages
#
# Revision 1.58  2004/02/13 20:12:44  bruno
# added support for LVM tags
#
# Revision 1.57  2004/02/07 00:10:07  fds
# Rollback to version 1.55.
#
# Revision 1.55  2004/02/03 01:52:05  fds
# More flexible yet. Can now call out multiple individual sections.
#
# Revision 1.54  2004/02/02 18:37:03  fds
# Support for Wide Area installs. New wanKickstart() method in kcgi issues
# a small ks file with external roll url followed by the installclass, and
# thats it.
#
# Kgen now knows how to only output the installclass.
#
# I dont love this code, but it is the first step.
#
# Revision 1.53  2003/11/13 04:55:02  mjk
# remove self.null for older python versions
#
# Revision 1.52  2003/11/06 01:00:00  mjk
# use file tag for logging
#
# Revision 1.51  2003/10/16 22:14:14  fds
# Cleaning up after mason. :)
#
# Revision 1.50  2003/10/16 21:31:17  mjk
# arch attribute is now list based
#
# Revision 1.49  2003/10/15 22:19:47  bruno
# fixes for taroon
#
# Revision 1.48  2003/09/16 18:08:35  fds
# Using KickstartError in trinity. Errors go to stderr.
#
# Revision 1.47  2003/09/04 17:37:20  fds
# Small change to error message
#
# Revision 1.46  2003/08/26 23:17:29  mjk
# missing a newline in file output
#
# Revision 1.45  2003/08/26 22:44:20  mjk
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
# Revision 1.44  2003/08/20 21:12:19  mjk
# - run file tags in a subshell
# - probe lsmod for keyboard type
#
# Revision 1.43  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.42  2003/08/14 17:38:38  mjk
# AW fixes
#
# Revision 1.41  2003/08/09 00:58:11  fds
# Better and clearer exception handling.
# Needed when kpp fails.
#
# Revision 1.40  2003/07/31 17:51:12  bruno
# removed debug statements
#
# Revision 1.39  2003/07/31 17:50:49  bruno
# one-liner that fixes updating the same configuration file
#
# Revision 1.38  2003/07/28 18:40:57  phil
# updated checking in files to RCS
#
# Revision 1.37  2003/07/25 00:00:29  phil
# Added putting config files into repository before changing
# them.
#
# Revision 1.36  2003/07/22 21:30:19  fds
# No extra newlines in file tag output.
#
# Revision 1.35  2003/07/21 19:37:57  fds
# Simplified kgen (regular append) with support for owner,
# perms, and vars=literal
#
# Revision 1.34  2003/07/21 19:17:29  fds
# NOT USED - Fancy Append.
#
# Revision 1.32  2003/07/17 22:23:56  fds
# Added 'owner' and 'perms' file attributes
#
# Revision 1.31  2003/07/16 20:56:20  fds
# New append-once fileMode attribute to <file> tags.
#
# Revision 1.30  2003/07/07 20:16:52  bruno
# updates for rolls
#
# Revision 1.29  2003/05/22 16:36:35  mjk
# copyright
#
# Revision 1.28  2003/05/21 18:57:31  mjk
# grid integration checkpoint
#
# Revision 1.27  2003/04/28 23:51:09  mjk
# who knows
#
# Revision 1.26  2003/04/28 21:52:51  mjk
# added order section
#
# Revision 1.25  2003/04/24 16:59:41  mjk
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
# Revision 1.24  2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.23  2002/11/07 18:13:44  mjk
# ia64 changes
#
# Revision 1.22  2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.21  2002/09/26 11:29:47  bruno
# fixed a bug in the architecture processing
#
# Revision 1.20  2002/07/03 23:33:11  bruno
# 7.3 fixes
#
# Revision 1.19  2002/06/28 18:18:49  mjk
# checkpoint for XML vs SQL stuff
# might even work
#
# Revision 1.18  2002/06/17 19:50:02  bruno
# 7.3-isms
#
# Revision 1.17  2002/06/11 20:20:28  mjk
# Added support for release tag
#
# Revision 1.16  2002/02/25 19:08:43  mjk
# Negative package resolution for CDROM and CGI kickstart generation.  I
# lost a single line of python code in kpp that fixed this but it didn't
# get checked in.  Backed out of Greg's code and fixed my screw up.
#
# Revision 1.13  2002/02/15 23:44:23  mjk
# - Added netscape to frontend
# - Move package trimming
#
# Revision 1.12  2002/02/14 02:12:29  mjk
# - Removed CD copy gui code from insert-ethers
# - Added CD copy code back to install.xml (using rocks-dist)
# - Added copycd command to rocks-dist
# - Added '-' packages logic to kgen
# - Other file changed to support above
#
# Revision 1.11  2002/02/12 23:48:51  mjk
# - Broken (just a checkpoint)
#
# Revision 1.10  2002/02/06 21:22:44  bruno
# all the little things that releases find ...
#
# Revision 1.9  2002/02/05 16:47:42  bruno
# support for deselecting packages
#
# Revision 1.8  2002/01/18 23:27:58  bruno
# updates for 7.2
#
# Revision 1.7  2001/12/03 21:27:59  bruno
# added support to understand the 'partition' flag in the clearpart and part
# tags.
#
# Revision 1.6  2001/11/09 23:50:53  mjk
# - Post release ia64 changes
#
# Revision 1.5  2001/09/14 21:45:42  mjk
# - Testing on ia32 compute nodes
# - A CGI kickstart takes 5 seconds
# - Working on ia64 compute nodes
#
# Revision 1.4  2001/09/10 18:26:38  mjk
# *** empty log message ***
#
# Revision 1.3  2001/09/05 00:27:16  mjk
# main and packages section is correct for compute nodes
#
# Revision 1.2  2001/08/21 01:52:39  mjk
# - <module> tag now prevent multiple inclusion
# - add dot support (ATT graph tool, just changed to GNU, we ship it now)
# - moved kickstart.cgi from rocks-dist RPM over here (called kcgi.py)
# - added <tree><node> tags
#

from __future__ import print_function
import os
import sys
import string
import stack.gen
import stack.file
import stack.gen
import stack.app
from xml.sax._exceptions     import SAXParseException
from stack.util import KickstartError


class App(stack.app.Application):

	def __init__(self, argv):
		stack.app.Application.__init__(self, argv)
		self.usage_name		= 'Kickstart Generator'
		self.usage_version	= '@VERSION@'
		self.sections		= []

		self.os = os.uname()[0].lower()
		if self.os == 'linux':
			self.os = 'redhat'
		osGenerator = getattr(stack.gen, 'Generator_%s' % self.os)
		self.generator = osGenerator()		
		self.generator.setArch(self.getArch())
		self.generator.setOS(self.os)
	
		self.getopt.s.extend([('a:', 'architecture')])
		self.getopt.l.extend([('arch=', 'architecture'),
				      ('section=', 'name'),
				      ('postonly', 'show post'),
				      ])

	def usageTail(self):
		return ' [file]'

	def parseArg(self, c):
		if stack.app.Application.parseArg(self, c):
			return 1
		elif c[0] in ('-a', '--arch'):
			self.generator.setArch(c[1])
		elif c[0] == '--section':
			self.sections += c[1].split()
		elif c[0] == '--postonly':
			self.sections.append('post')
		else:
			return 0
		return 1


	def run(self):

        	if self.args:
			file = open(self.args[0], 'r')
		else:
			file = sys.stdin
		
		self.generator.parse(file.read())

		print('#')
		print('# %s version %s' % (self.usage_name, self.usage_version))
		print('#')

		sections = self.sections
		if not sections:
			sections = [
				'order',
				'debug',
				'main',
				'packages',
				'pre',
				'post',
				]
		list = []
		for s in sections:
			list += self.generator.generate(s)

		for line in list:
			print(line.rstrip())


app = App(sys.argv)
app.parseArgs()
try:
	app.run()
except KickstartError as msg:
	sys.stderr.write("kgen error - %s\n" % msg)
	sys.exit(-1)

except SAXParseException as msg:
	sys.stderr.write("kgen XML parse exception: %s\n" % msg)
	sys.exit(-1)


