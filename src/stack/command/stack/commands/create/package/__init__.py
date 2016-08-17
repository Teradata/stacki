# @SI_Copyright@
#                               stacki.com
#                                  v3.3
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


import os
import tempfile
import shutil
import stack
import stack.commands
import string
		
class Command(stack.commands.create.command):
	"""
	Create a RedHat or Solaris package from a given directory.  The
	package will install files in either the same location as the given
	directory, or a combination of the directory basename and the
	provided prefix.

	<param type='string' name='dir'>
	The source directory of the files used to create the OS-specific
	package.
	</param>

	<param type='string' name='name'>
	The name of the package
	</param>

	<param type='string' name='prefix'>
	The prefix pathname prepended to the base name of the source
	directory.
	</param>

	<param type='string' name='version'>
	Version number of the created package (default is current version of Rocks+)
	</param>

	<param type='string' name='release'>
	Release number of the created package (default is '1')
	</param>

	<param type='string' name='rpmextra'>
	Extra RPM directives. These are comma-seperated values that
	are put into the spec files when the RPM is created
	</param>

	<example cmd='create package dir=/opt/stream name=stream'>
	Create a package named stream in the current directory using the
	contents of the /opt/stream directory.  The resulting package will
	install its files at /opt/stream.
	</example>

	<example cmd='create package dir=/opt/stream name=localstream prefix=/usr/local'>
	Create a package named localstream in the current directory using the
	contents of the /opt/stream directory.  The resulting package will
	install its files at /usr/local/stream.
	</example>
	
	<example cmd='createpackage dir=/opt/stream name=stream rpmextra="Requires: iperf, AutoReqProv: no"'>
	Creates the steam package with an RPM "requires" directive on iperf,
	and disables automatic dependency resolution for the package.
	</example>
	"""

	def run(self, params, args):
		dir = None

		(name, dir, prefix, version,
			release, rpmextra) = self.fillParams([
				('name', None, True),
				('dir', None, True),
				('prefix',),
				('version', stack.version),
				('release', '1'),
				('rpmextra','AutoReqProv: no'),
			])

		rocksRoot = os.environ['ROCKSBUILD']

		if not prefix:
			prefix = os.path.split(dir)[0]
		
		tmp = tempfile.mktemp()
		os.makedirs(tmp)
		shutil.copy(os.path.join(rocksRoot,'etc', 'create-package.mk'),
			    os.path.join(tmp, 'Makefile'))
		cwd = os.getcwd()
		os.chdir(tmp)

		file = open(os.path.join(tmp, 'version.mk'), 'w')
		file.write('NAME=%s\n' % name)
		file.write('VERSION=%s\n' % version)
		file.write('RELEASE=%s\n' % release)
		file.write('PREFIX=%s\n' % prefix)
		file.write('SOURCE_DIRECTORY=%s\n' % dir)
		file.write('DEST_DIRECTORY=%s\n' % cwd)

		# Create the RPM.EXTRAS directive that will add
		# extra information to the specfile
		rpm_extras = map(string.strip, rpmextra.split(','))
		rpmextra = string.join(rpm_extras, '\\\\n')
		file.write("RPM.EXTRAS=\"%s\"\n" % rpmextra)
		file.close()

		for line in os.popen('make dir2pkg').readlines():
			self.addText(line)

		shutil.rmtree(tmp)
		

