# This file was originally authored by
# Brandon Davidson from the University of Oregon.
# The Rocks Developers thank Brandon for his contribution.
#
# @SI_Copyright@
#                               stacki.com
#                                  v3.3
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


import os
import stat
import time
import sys
import string
import stack.commands
from stack.exception import *


class Command(stack.commands.RollArgumentProcessor,
	stack.commands.remove.command):
	"""
	Remove a pallet from both the database and filesystem.	

	<arg type='string' name='pallet' repeat='1'>
	List of pallets. This should be the pallet base name (e.g., base, hpc,
	kernel).
	</arg>
	
	<param type='string' name='version'>
	The version number of the pallet to be removed. If no version number is
	supplied, then all versions of a pallet will be removed.
	</param>
	
	<param type='string' name='release'>
	The release id of the pallet to be removed. If no release id is
	supplied, then all releases of a pallet will be removed.
	</param>

	<param type='string' name='arch'>
	The architecture of the pallet to be removed. If no architecture is
	supplied, then all architectures will be removed.
	</param>

	<example cmd='remove pallet kernel'>
	Remove all versions and architectures of the kernel pallet.
	</example>
	
	<example cmd='remove pallet ganglia version=5.0 arch=i386'>
	Remove version 5.0 of the Ganglia pallet for i386 nodes.
	</example>
	
	<related>add pallet</related>
	<related>enable pallet</related>
	<related>disable pallet</related>
	<related>list pallet</related>
	<related>create pallet</related>
	"""		

	def run(self, params, args):
		self.beginOutput()

                (arch, OS) = self.fillParams([
                        ('arch', '%'),
                        ('os','%')
                        ])

                if len(args) < 1:
                        raise ArgRequired(self, 'pallet')

		for (roll, version, release) in self.getRollNames(args, params):
			rows = self.db.execute("""
				select os, arch from rolls where
				name = '%s' and version = '%s' and
				arch like '%s' and os like '%s'
				""" % (roll, version, arch, OS))

			if rows == 0: # empty table is OK
				continue

			# Remove each arch's instance of this pallet version
			for (thisos, thisarch,) in self.db.fetchall():
				self.clean_pallet(roll, version, release, thisos,
					thisarch)

		self.endOutput(padChar='')


	def clean_pallet(self, roll, version, release, OS, arch):
		""" Remove pallet files and database entry for this arch. Calls 
		the Host OS specific function for proper filesystem cleanup. """

		self.addOutput('', 'Removing %s %s-%s-%s-%s pallet ...' %
			(roll, version, release, OS, arch))

		prefix = '/export/stack/pallets'

        	os.system('/bin/rm -rf %s' %
			os.path.join(prefix, roll, version, release, OS, arch))

		f = [ prefix, roll, version, release, OS ]
		i = len(f) - 1

		while f != [ prefix ]:
			d = '/'.join(f)

                        try:
				if os.listdir(d):
					#
					# this directory has at least one element in
					# it, so let's keep it (that is, let's exit
					# this loop).
					#
					break
                        except:
                                break

			os.system('/bin/rm -rf %s' % d)

			f.remove(f[i])

			i -= 1
			if i <= 0:
				break

		# Remove pallet from database as well
		# we need the id before deleting, as it's a fkey
		self.db.execute("""
			select id from rolls where
			name = '%s' and version = '%s' and rel = '%s' and
			arch = '%s' and os = '%s'
			""" % (roll, version, release, arch, OS))

		doomed_pallet_id = self.db.fetchone()

		# remove from the list of pallets and stacks
		self.db.execute("""
			delete from rolls where
			id = '%s'
			""" % doomed_pallet_id)
		self.db.execute("""
			delete from stacks where
			roll = '%s'
			""" % doomed_pallet_id)

		# Regenerate stacki.repo
		os.system("""
			/opt/stack/bin/stack report host yum localhost | 
			/opt/stack/bin/stack report script | 
			/bin/sh
			""")

