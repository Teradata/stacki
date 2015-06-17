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
# Revision 1.9  2010/09/07 23:53:00  bruno
# star power for gb
#
# Revision 1.8  2010/05/27 00:11:32  bruno
# firewall fixes
#
# Revision 1.7  2010/04/30 22:03:25  bruno
# 'rocks report script' can now process attributes
#
# Revision 1.6  2009/05/01 19:07:02  mjk
# chimi con queso
#
# Revision 1.5  2009/04/27 18:03:33  bruno
# remove dead setRCS* and getRCS* functions
#
# Revision 1.4  2009/03/26 23:58:16  anoop
# "rocks report script" now supports Solaris
#
# Revision 1.3  2008/10/18 00:55:56  mjk
# copyright 5.1
#
# Revision 1.2  2008/09/22 20:20:42  bruno
# change 'rocks config host interface|network' to
# change 'rocks report host interface|network'
#
# Revision 1.1  2008/07/23 00:01:06  bruno
# tweaks
#
#
#

import sys
import tempfile
import os.path
import stack.commands
import stack.gen

class Command(stack.commands.report.command):
	"""
	Take STDIN XML input and create a shell script that can be executed
	on a host.

	<param optional='1' type='string' name='os'>
	The OS type.
	</param>

	<param optional='1' type='string' name='arch'>
	The architecture type.
	</param>

	<param optional='1' type='string' name='attrs'>
	Attributes to be used while building the output shell script.
	</param>

	<example cmd='report host interface compute-0-0 | rocks report script'>
	Take the network interface XML output from 'rocks report host interface'
	and create a shell script.
	</example>
	"""

	def scrub(self, xml):
		filename = tempfile.mktemp()

		file = open(filename, 'w')
		file.write(xml)
		file.close()

		scrubed = ''
		cmd = 'xmllint --nocdata %s' % (filename)
		for line in os.popen(cmd).readlines():
			scrubed += line
		
		os.remove(filename)

		return scrubed
		

	def runXML(self, xml):
		list = []

		self.generator.parse(xml)
		section_name = 'post'
		if self.os == 'sunos':
			section_name = 'finish'

		# The generate command returns a list of
		# tuples of the form (text, rollname, nodefile, rollcolor)
		list += self.generator.generate(section_name)
		for line in list:
			# For the following we only need text
			if line[0:5] == '%post':
				continue

			if line == '%end':
				continue

			self.addOutput('', line.rstrip())


	def run(self, params, args):
		self.os, self.arch, attributes = self.fillParams([
			('os', self.os),
			('arch', self.arch),
			('attrs', )
			])

		c_gen = getattr(stack.gen,'Generator_%s' % self.os)
		self.generator = c_gen()
		self.generator.setArch(self.arch)
		self.generator.setOS(self.os)

		starter_tag = 'kickstart'
		if self.os == 'sunos':
			starter_tag = 'jumpstart'

		self.beginOutput()

		xml = '<?xml version="1.0" standalone="no"?>\n'

		if attributes:
			attrs = eval(attributes)
			xml += '<!DOCTYPE rocks-graph [\n'
			for (k, v) in attrs.items():
				xml += '\t<!ENTITY %s "%s">\n' % (k, v)
			xml += ']>\n'

		xml += '<%s>\n' % starter_tag
		if self.os == 'sunos':
			xml += '<post chroot="no">\n'
		else:
			xml += '<post>\n'

		for line in sys.stdin.readlines():
			xml += line

		xml += '</post>\n'
		xml += '</%s>\n' % starter_tag

		self.runXML(self.scrub(xml))

		self.endOutput(padChar='')

