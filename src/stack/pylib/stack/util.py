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
# Revision 1.16  2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.15  2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.14  2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.13  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.12  2007/06/23 04:03:24  mjk
# mars hill copyright
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
# Revision 1.7  2005/09/16 01:02:21  mjk
# updated copyright
#
# Revision 1.6  2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.5  2005/05/24 21:21:57  mjk
# update copyright, release is not any closer
#
# Revision 1.4  2005/04/29 01:14:25  mjk
# Get everything in before travel.  Rocks-roll is looking pretty good and
# can now build the os roll (centos with updates).  It looks like only the
# first CDROM of our os/centos roll is needed with 3 extra disks.
#
# - rocks-dist cleanup (tossed a ton of code)
# - rocks-roll growth (added 1/2 a ton of code)
# - bootable rolls do not work
# - meta rolls are untested
# - rocks-dist vs. rocks-roll needs some redesign but fine for 4.0.0
#
# Revision 1.3  2005/03/31 22:40:11  mjk
# spinner cleans up after itself
#
# Revision 1.2  2005/03/25 22:55:28  fds
# Added mjk's startSpinner(), moved from build.py
#
# Revision 1.1  2005/03/01 00:22:08  mjk
# moved to base roll
#
# Revision 1.15  2004/07/20 19:47:20  fds
# 411 group support. Also cleaned out some depricated options.
#
# Revision 1.14  2004/04/28 21:05:44  fds
# Rocks-dist optimization for cross-kickstarting. Do not need the awkward
# --genhdlist flag anymore.
# o Will automatically find the native genhdlist executable, but
# o requires the native dist be made first.
#
# Revision 1.13  2004/04/09 15:19:06  fds
# Incorporating characters() method for parsing data between start/end tags.
#
# Revision 1.12  2004/03/25 03:15:48  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.11  2004/03/20 03:31:24  fds
# A class to make writing our style of XML parsers easy.
#
# Revision 1.10  2004/01/29 18:58:43  mjk
# added more kpp exceptions
#
# Revision 1.9  2003/09/16 18:09:01  fds
# Added KickstartError
#
# Revision 1.8  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.7  2003/05/22 16:39:28  mjk
# copyright
#
# Revision 1.6  2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.5  2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.4  2002/02/21 21:33:28  bruno
# added new copyright
#
# Revision 1.3  2001/05/09 20:17:22  bruno
# bumped copyright 2.1
#
# Revision 1.2  2001/04/27 01:08:50  mjk
# - Created working 7.0 and 7.1 distibutions (in same tree even)
# - Added symlink() method to File object.  Trying to get the File object
#   to make the decision on absolute vs. relative symlinks.  So far we are
#   absolute everywhere.
# - Still missing CD making code.  Need to figure out how to read to
#   comps files using RedHat's anaconda python code.  Then we can decide
#   which RPMs can go on the second CD based on what is required in the
#   kickstart files.
#
# Revision 1.1  2001/04/18 01:20:38  mjk
# - Added build.py, util.py modules
#
# - Getting closer.  I'm happy with the object model for building
# mirrors, and this will extend well to build the distributions.
#
# - Seriously needs a design document.
#

from __future__ import print_function
import warnings
warnings.filterwarnings("ignore")


import os
import sys
import popen2
from xml.sax import handler

# An exception for Kickstart builder trinity: kcgi, kgen, kpp

class KickstartError(Exception):
	pass

class KickstartGraphError(KickstartError):
	pass

class KickstartNodeError(KickstartError):
	pass

# Simulate 'C' struct, but in Pythons funky dynamic way e.g.:
#
#	foo = Stuct()
#	foo.bar = 1
#	foo.oof = foo.bar
#
# cool, huh?

class Struct:
    pass


def list2str(list):
    s = ''
    for e in list:
        s = s + e
    return s


def listcmp(l1, l2):
    return map(lambda a,b: a==b, l1, l2)

def listdup(e, n):
    l = []
    for i in range(0, n):
        l.append(e)
    return l


def list_isprefix(l1, l2):
    l = listcmp(l1, l2)
    for i in range(0, len(l1)):
        if not l[i]:
            return 0
    return 1
        


def getNativeArch():
	"""Returns the canotical arch as reported by the operating system"""
	
	arch = os.uname()[4]
	if arch in [ 'i386', 'i486', 'i586', 'i686']:
		arch = 'i386'
	return arch


def mkdir(newdir):
	"""Works the way a good mkdir should :)
		- already exists, silently complete
		- regular file in the way, raise an exception
		- parent directory(ies) does not exist, make them as well
		From Trent Mick's post to ASPN."""
	if os.path.isdir(newdir):
		pass
	elif os.path.isfile(newdir):
		raise OSError("a file with the same name as the desired " \
					"dir, '%s', already exists." % newdir)
	else:
		head, tail = os.path.split(newdir)
		if head and not os.path.isdir(head):
			mkdir(head)
		if tail:
			os.mkdir(newdir)



class ParseXML(handler.ContentHandler,
		  handler.DTDHandler,
		  handler.EntityResolver,
		  handler.ErrorHandler):
	"""A helper class to for XML parsers. Uses our
	startElement_name style."""

	def __init__(self, app=None):
		handler.ContentHandler.__init__(self)
		self.app = app
		self.text = ''
		

	def startElement(self, name, attrs):
		"""The Mason Katz school of parsers. Make small functions
		instead of monolithic case statements. Easier to override and
		to add new tag handlers."""
		try:
			f = getattr(self, "startElement_%s" % name)
			f(name, attrs)
		except AttributeError:
			return


	def endElement(self, name):
		try:
			f = getattr(self, "endElement_%s" % name)
			f(name)
		except AttributeError:
			return


	def characters(self, s):
		self.text += s


def system(cmd, type='standard'):
	print(cmd)

	if type == 'spinner':
		return startSpinner(cmd)
	else:
		return os.system(cmd)
		

def startSpinner(cmd):
	"""This used to just be a system() but now we
	control the child output to keep the status
	on one line using stupid CR terminal tricks.
	We even add a way cool spinny thing in
	column zero just to be l33t!
	
	Does not show standard error output."""

	r, w, e = popen2.popen3(cmd)
	currLength  = 0
	prevLength  = 0
	spinChars   = '-\|/'
	spinIndex   = 0
	while 1:
		line = e.readline()
		if not line:
			break
		if len(line) > 79:
			data = line[0:78]
		else:
			data = line[:-1]
		currLength = len(data)
		pad = ''
		for i in range(0, prevLength - currLength):
			pad = pad + ' '
		spin  = spinChars[spinIndex % len(spinChars)]
		spinIndex = spinIndex + 1
		print(spin + data + pad + '\r', end=' ')
		prevLength = currLength
		sys.stdout.flush()
	r.close()
	w.close()
	e.close()
		
	# Cleanup screen when done
		
	pad = ''
	for i in range(0,78):
		pad = pad + ' '
	print('\r%s\r' % pad, end=' ')
	

def prettyNumber(x):
	try:
		a = float(x)
	except:
		return None

	if a >= 1024**7:
		size = '%.02fZ' % (a / 1024**7)
	elif a >= 1024**6:
		size = '%.02fE' % (a / 1024**6)
	elif a >= 1024**5:
		size = '%.02fP' % (a / 1024**5)
	elif a >= 1024**4:
		size = '%.02fT' % (a / 1024**4)
	elif a >= 1024**3:
		size = '%.02fG' % (a / 1024**3)
	elif a >= 1024**2:
		size = '%.02fM' % (a / 1024**2)
	elif a >= 1024:
		size = '%.02fK' % (a / 1024)
	else:
		size = '%.02f' % a

	return size

