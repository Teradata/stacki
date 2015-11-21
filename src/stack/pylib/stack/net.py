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
# Revision 1.13  2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.12  2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.11  2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.10  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.9  2007/06/23 04:03:24  mjk
# mars hill copyright
#
# Revision 1.8  2006/09/11 22:47:23  mjk
# monkey face copyright
#
# Revision 1.7  2006/08/10 00:09:41  mjk
# 4.2 copyright
#
# Revision 1.6  2006/01/16 06:49:00  mjk
# fix python path for source built foundation python
#
# Revision 1.5  2005/10/12 18:08:42  mjk
# final copyright for 4.1
#
# Revision 1.4  2005/09/16 01:02:21  mjk
# updated copyright
#
# Revision 1.3  2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.2  2005/05/24 21:21:57  mjk
# update copyright, release is not any closer
#
# Revision 1.1  2005/03/01 00:22:08  mjk
# moved to base roll
#
# Revision 1.5  2004/12/09 01:18:47  fds
# More resiliant to failures, dont complain as much.
#
# Revision 1.4  2004/03/25 03:15:48  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.3  2003/10/30 02:32:59  fds
# Support for rocks-private-interface
#
# Revision 1.2  2003/10/17 18:37:46  fds
# I dont expect people to know what a 'private' network interface means.
#
# Revision 1.1  2003/09/24 23:24:13  fds
# A rocks application that knows things about the cluster network.
#
#

import os
import sys
import stack.app
import gmon.Network


class Application(stack.app.Application):
	"""A derivative of a rocks application that knows certain things
	about the cluster network. Used by 411 and mpdring."""

	def __init__(self, argv=None):
		stack.app.Application.__init__(self, argv)
		self.rcfileHandler = RCFileHandler
		self.master_network = ''
		self.master_netmask = ''
		
		
	def privateInterface(self):
		"""Returns the name of the network interface on our private
		cluster network. We use a hint from our rocksrc config file to
		guide our search for the 'right' one. Defaults to eth0 if hint
		is missing.
		
		Returned interface is guaranteed to be up. If nothing suitable
		is up, we raise an Exception."""
		
		# I wrote the Network module in C just for this purpose.  The
		# netcmp() function works like strcmp(), where 0 means args are
		# the same.

		intfs = gmon.Network.interfaces()

		if self.master_network:
			target_net = "%s/%s" % \
				(self.master_network, self.master_netmask)
			for i in intfs:
				if not gmon.Network.netcmp(intfs[i], target_net):
					return i

		# We have no hint, check default.
		
		if 'eth0' in intfs:
			return 'eth0'
			
		raise Exception("Your private interface (eth0) is down")
						

	def privateIP(self):
		"""Returns the IP address of the interface on our private
		cluster network."""

		intfs = gmon.Network.interfaces()
		
		# Interface value is in libdnet format: "addr/mask"
		return intfs[self.privateInterface()].split('/')[0]
			



class RCFileHandler(stack.app.RCFileHandler):
	"""Interprets the 'PrivateNetwork' tag to determine
	what interface we should use to communicate with clients."""

	def __init__(self, application):
		stack.app.RCFileHandler.__init__(self, application)

	def startElement_PrivateNetwork(self, name, attrs):
		self.app.master_network = attrs.get('id')
		self.app.master_netmask = attrs.get('mask')

