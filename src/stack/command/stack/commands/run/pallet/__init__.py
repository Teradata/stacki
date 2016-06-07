# @SI_Copyright@
#                             www.stacki.com
#                                  v3.1
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
import string
import popen2
import stack.gen
import stack.file
import stack.commands
import tempfile
import sys
from xml.dom.ext.reader import Sax2
from stack.exception import *

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

		(dryrun, ) = self.fillParams([ ('dryrun', 'true')])
		
                dryrun = self.str2bool(dryrun)
                
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

		rpms = set()
		for line in gen.generate('packages'):
			if line.find('%package') == -1 and line.find('%end') == -1:
				rpms.add(line)
		if rpms:
			script.append('yum install -y %s' % ' '.join(rpms))

		cur_proc = False
		for line in gen.generate('post'):
			if not line.startswith('%post') and not line.startswith('%end'):
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
			# skip lines that start with '%post' or '%end'
			#
			if line[0:5] == '%post' or line[0:4] == '%end':
				continue

			script.append(line)

		if dryrun:
			self.addText(string.join(script, '\n'))
		else:
			os.system(string.join(script, '\n'))

