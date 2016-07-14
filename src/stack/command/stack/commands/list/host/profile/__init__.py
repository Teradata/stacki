# @SI_Copyright@
#                               stacki.com
#                                  v3.2
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
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

import sys
import stack.commands
import stack.gen
from stack.exception import *


class Command(stack.commands.list.host.command):
	"""
	Outputs a XML wrapped Kickstart/Jumpstart profile for the given hosts.
	If not, profiles are listed for all hosts in the cluster. If input is
	fed from STDIN via a pipe, the argument list is ignored and XML is
	read from STDIN.  This command is used for debugging the Rocks
	configuration graph.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host profile compute-0-0'>
	Generates a Kickstart/Jumpstart profile for compute-0-0.
	</example>

	<example cmd='list host xml compute-0-0 | rocks list host profile'>
	Does the same thing as above but reads XML from STDIN.
	</example>
	"""

	MustBeRoot = 1

	# Annotation function. If annotation is required
	# return a list of [text, rollname, nodefile, rollcolor]
	# Otherwise simply return the text string
	def annotate(self, o):
		if type(o) == str or type(o) == unicode:
			if self.annotation:
				return [o, None, None, None]
			else:
				return o
		if type(o) == tuple:
			if self.annotation:
				return list(o)
			else:
				return o[0]
			
	def run(self, params, args):
		"""Generate the OS specific profile file(s) in a single XML
		stream (e.g. Kickstart or Jumpstart).  If a host argument
		is provided use it, otherwise assume the cooked XML is
		on stdin."""

		# By default, print all sections of kickstart/jumpstart file
		(section, annotation, os) = self.fillParams([
			('section','all'),
			('annotate','false'),
			('os','redhat'),
			])

		self.section = section
		self.os	     = os
		self.annotation=self.str2bool(annotation)
		self.beginOutput()

		hosts = self.getHostnames(args)
		if len(args) == 0:
			host = 'localhost'
		# If we're reading from input
		if not sys.stdin.isatty():
			xml = ''
			for line in sys.stdin.readlines():
				xml += line
			self.addOutput('localhost',
				self.annotate(
				'<?xml version="1.0" standalone="no"?>'))
			self.runImplementation(self.os, ('localhost', xml))

		# If no input is given
		else:		
			for host in self.getHostnames(args):
				self.os = self.db.getHostOS(host)
				self.addOutput(host,
					self.annotate(
					'<?xml version="1.0" standalone="no"?>'
					))
				self.runImplementation(self.os, (host, None))

		if self.annotation:
			self.endOutput(padChar='', header=[
					'host','output','pallet',
					'nodefile', 'color'])
		else:
			self.endOutput(padChar='')
