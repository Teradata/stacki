# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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

from __future__ import print_function
import os
import sys
import string
import tempfile
import shutil
import stack.file
import stack.commands


class Command(stack.commands.add.command):
	"""
	Insert a copyright for each file under a directory.

	This a used exclusively by stacki developers to ensure all files
	have current copyright statements.
	"""

	def iter(self, dir, file, root):
		try:
			#
			# skip source control files
			#
			if '.git' in file.getFullName().split('/'):
				return
		except:
			pass

		try:
			fin = open(file.getFullName(), 'r')
		except IOError:
			return

		tmp = tempfile.mktemp()
		fout = open(tmp, 'w')
		
		state  = 0	# 0 - outside block, 1 - inside block
		blocks = 0	# number of copyright blocks found
		for line in fin.readlines():
			pos = string.find(line, self.pattern[state])
			if pos >= 0:
				state = state ^ 1
				if not state:
					blocks += 1
				else:
			                prefix = line[0:pos]
			                suffix = line[pos+len(self.pattern[0]):]
					fout.write(line)
					for text in self.copyright:
						fout.write('%s%s%s' % (
							prefix,
							text,
							suffix))
			if not state:
				fout.write(line)
			
		fin.close()
		fout.close()
		
		# Commit the replaced text only if a complete copyright
		# block was found.  This will make sure a single copyright
		# tag in a file does not cause all the code to be lost.
		
		if blocks:
			print(file.getFullName())
			shutil.copymode(file.getFullName(), tmp)
			try:
				shutil.copyfile(tmp, file.getFullName())
			except IOError, msg:
				pass
		os.unlink(tmp)
				

	def run(self, params, args):
		
		path = os.path.dirname(__file__)
		copyright = {}
		copyright['stacki-long']  = os.path.join(path, 'copyright-stacki')
		copyright['stacki-short'] = os.path.join(path, 'copyright-stacki-short')
		copyright['rocks-long']   = os.path.join(path, 'copyright-rocks')
		copyright['rocks-short']  = os.path.join(path, 'copyright-rocks-short')

		for (k,v) in copyright.items():
			file = open(v, 'r')
			copyright[k] = []
			for line in file.readlines():
				copyright[k].append(line[:-1])

		# We breakup the string below to protect this code segment
		# for insert-copyright detecting the tags.  Otherwise we
		# could not run on ourselves.
		self.tree = stack.file.Tree('../../..')
		
		print('Inserting stacki copyright into source code files...')
		self.pattern   = [ '@' + 'SI_Copyright@', '@' + 'SI_Copyright@' ]
		self.copyright = copyright['stacki-long']
		self.tree.apply(self.iter)

		print('Inserting stacki copyright into XML files...')
		self.pattern = [ '<' + 'si_copyright>', '<' + '/si_copyright>' ]
		self.copyright = copyright['stacki-short']
		self.tree.apply(self.iter)

		print('Inserting rocks copyright into source code files...')
		self.pattern   = [ '@' + 'Copyright@', '@' + 'Copyright@' ]
		self.copyright = copyright['rocks-long']
		self.tree.apply(self.iter)

		print('Inserting rocks copyright into XML files...')
		self.pattern = [ '<' + 'copyright>', '<' + '/copyright>' ]
		self.copyright = copyright['rocks-short']
		self.tree.apply(self.iter)

