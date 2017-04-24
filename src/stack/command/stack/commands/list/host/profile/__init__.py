# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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
import string
from xml.sax import make_parser
import stack.commands
import stack.gen
from stack.exception import *

class implementation(stack.commands.Implementation):

        def generator(self):
                pass

        def chapter(self, generator, profile):
                pass


	def run(self, (xmlinput, profileType, chapter)):

                profile     = []
		generator   = self.generator()

                generator.setProfileType(profileType)
		generator.parse(xmlinput)

                profile.append('<?xml version="1.0" standalone="no"?>')
                profile.append('<profile-%s>' % generator.getProfileType())

                profile.append('<chapter name="stacki">')
                for line in generator.generate('stacki'):
	                profile.append('%s' % line)
		profile.append('</chapter>')

		profile.append('<chapter name="meta">')
                profile.append('\t<section name="order">')
                for line in generator.generate('order'):
	                profile.append('%s' % line)
                profile.append('\t</section>')
                profile.append('\t<section name="debug">')
                for line in generator.generate('debug'):
                        profile.append(line)
                profile.append('\t</section>')
		profile.append('</chapter>')

                self.chapter(generator, profile)

                profile.append('</profile-%s>' % generator.getProfileType())

                if chapter:
			parser  = make_parser()
			handler = stack.gen.ProfileHandler()

			parser.setContentHandler(handler)
                        for line in profile:
                                parser.feed('%s\n' % line)

                        profile = handler.getChapter(chapter)

                for line in profile:
                        self.owner.addOutput(None, line)


class Command(stack.commands.list.host.command):
	"""
        Outputs a XML wrapped installer profile for the given hosts.

        If no hosts are specified the profiles for all hosts are listed.
	
        If input is fed from STDIN via a pipe, the argument list is
	ignored and XML is read from STDIN.  This command is used for
	debugging the Stacki configuration graph.

	<arg optional='1' type='string' name='host'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host profile backend-0-0'>
	Generates a Kickstart profile for backend-0-0.
	</example>

	<example cmd='list host xml backend-0-0 | stack list host profile'>
	Does the same thing as above but reads XML from STDIN.
	</example>

        """

	MustBeRoot = 1

	def run(self, params, args):

		(profile, chapter) = self.fillParams([
                        ('profile', 'native'),
                        ('chapter', None) ])

		xmlinput  = ''
                osname    = None

		# If the command is not on a TTY, then try to read XML input.

		if not sys.stdin.isatty():
			for line in sys.stdin.readlines():
                                if line.find('<stack:profile stack:os="') == 0:
                                        osname = line.split()[1][9:].strip('"')
				xmlinput += line
                if xmlinput and not osname:
                        raise CommandError(self, "OS name not specified in profile")

		self.beginOutput()

		# If there's no XML input, either we have TTY, or we're running
		# in an environment where TTY cannot be created (ie. apache)

		if not xmlinput:
                        hosts = self.getHostnames(args)
                        if len(hosts) != 1:
                                raise ArgUnique(self, 'host')
                        host = hosts[0]

                        osname	 = self.db.getHostOS(host)
                        xmlinput = self.command('list.host.xml', [ host ])

                        self.runImplementation(osname, (xmlinput, profile, chapter))

		# If we DO have XML input, simply parse it.

                else:
			self.runImplementation(osname, (xmlinput, profile, chapter))

		self.endOutput(padChar='', trimOwner=True)
