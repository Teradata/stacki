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
# Revision 1.8  2011/08/09 01:03:16  anoop
# If yum install fails due to dependency error,
# force install using rpm --nodeps
#
# Revision 1.6  2011/07/15 23:48:00  anoop
# Rocks run roll needs to honour the "--interpreter" flag
# to the post sections
#
# Revision 1.5  2011/07/13 18:36:29  anoop
# Honour .<arch> directive to yum install.
# When installing packages use,
# "yum install <package>" instead of "yum install <packagefile>.rpm"
#
# Revision 1.4  2011/01/24 22:47:34  mjk
# Use YUM instead of RPM for rocks run roll
# This fixes two issues
# 1) On 64bit we were not installing the 32bit RPMs
# 2) name.arch packages were not being installed
#
# Revision 1.3  2010/09/07 23:53:00  bruno
# star power for gb
#
# Revision 1.2  2009/05/01 19:07:02  mjk
# chimi con queso
#
# Revision 1.1  2009/03/06 22:34:16  mjk
# - added roll argument to list.host.xml and list.node.xml
# - kroll is dead, added run.roll
#

import os
import string
import popen2
import stack.gen
import stack.file
import stack.commands
import tempfile
import sys
from xml.dom.ext.reader import Sax2

rpm_force_template = """[ $? -ne 0 ] && \\
echo "# YUM failed - trying with RPM" && \\
rpm -Uvh --force --nodeps %s"""
	
class Command(stack.commands.run.command):
	"""
	Installs a pallet on the fly
	
	<arg optional='1' type='string' name='pallet' repeat='1'>
	List of pallets. This should be the pallet base name (e.g., base, hpc,
	kernel).
	</arg>

	<example cmd='run pallet viz'>		
	Installs the Viz pallet onto the current system.
	</example>
	"""

	def run(self, params, args):

		(dryrun, ) = self.fillParams([('dryrun', )])
		
		if dryrun:
			dryrun = self.str2bool(dryrun)
		else:
			dryrun = True
		
		script = []
		script.append('#!/bin/sh')

		rolls = []
		for roll in args:
			rolls.append(roll)
		if sys.stdin.isatty():
			xml = self.command('list.host.xml', [ 'localhost', 
				'pallet=%s' % string.join(rolls, ',') ])
		else:
			xml = sys.stdin.read()
		reader = Sax2.Reader()
		gen = getattr(stack.gen,'Generator_%s' % self.os)()
		gen.parse(xml)

		distPath = os.path.join(self.command('report.distribution')[:-1],
			'default')
                tree = stack.file.Tree(distPath)
		rpm_list = {}
		for file in tree.getFiles(os.path.join(self.arch, 
			'RedHat', 'RPMS')):
			if isinstance(file, stack.file.RPMFile):
				rpm_list[file.getBaseName()] = \
					file.getFullName()
				rpm_list["%s.%s" % (file.getBaseName(), \
					file.getPackageArch())] = \
						file.getFullName()
			
		rpms = []
		for line in gen.generate('packages'):
			if line.find('%package') == -1:
				rpms.append(line)
		for rpm in rpms:
			if rpm in rpm_list.keys():
				script.append('yum install -y %s' %
					rpm)
				script.append(rpm_force_template %
					rpm_list[rpm])


		cur_proc = False
		for line in gen.generate('post'):
			if not line.startswith('%post'):
				script.append(line)
			else:
				if cur_proc == True:
					script.append('__POSTEOF__')
					script.append('%s %s' % (interpreter,
						t_name))
					cur_proc = False
				try:
					i = line.split().index('--interpreter')
				except ValueError:
					continue
				interpreter = line.split()[i+1]
				t_name = tempfile.mktemp()
				cur_proc = True
				script.append('cat > %s << "__POSTEOF__"' %
					t_name)
		
		script.append('\n# Boot scripts\n')
		for line in gen.generate('boot'):
			#
			# skip lines that start with '%post'
			#
			if line[0:5] == '%post':
				continue

			script.append(line)

		if dryrun:
			self.addText(string.join(script, '\n'))
		else:
			os.system(string.join(script, '\n'))

