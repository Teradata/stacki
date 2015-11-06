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


import os
import stat
import time
import sys
import string
import stack.commands
from stack.exception import *


class Command(stack.commands.RollArgumentProcessor,
	stack.commands.enable.command):
	"""
	Enable an available pallet. The pallet must already be copied on the
	system using the command "stack add pallet".

	<arg type='string' name='pallet' repeat='1'>
	List of pallets to enable. This should be the pallet base name (e.g.,
	stacki, boss, os).
	</arg>
	
	<param type='string' name='version'>
	The version number of the pallet to be enabled. If no version number is
	supplied, then all versions of a pallet will be enabled.
	</param>

	<param type='string' name='release'>
	The release number of the pallet to be enabled. If no release number is
	supplied, then all releases of a pallet will be enabled.
	</param>

	<param type='string' name='arch'>
	If specified enables the pallet for the given architecture.  The default
	value is the native architecture of the host.
	</param>

	<param type='string' name='box'>
	The name of the box in which to enable the pallet. If no
	box is specified the pallet is enabled for the default box.
	</param>

	<example cmd='enable pallet kernel'>
	Enable the kernel pallet.
	</example>

	<example cmd='enable pallet ganglia version=5.0 arch=i386'>
	Enable version 5.0 the Ganglia pallet for i386 nodes.
	</example>

	<related>add pallet</related>
	<related>remove pallet</related>
	<related>disable pallet</related>
	<related>list pallet</related>
	<related>create pallet</related>
	"""		

	def run(self, params, args):
                if len(args) < 1:
                        raise ArgRequired(self, 'pallet')

                (arch, box) = self.fillParams([
                        ('arch', self.arch),
                        ('box', 'default')
                        ])

		rows = self.db.execute("""
			select * from boxes where name='%s'
			""" % box)
		if not rows:
                        raise CommandError(self, 'unknown box "%s"' % box)
		
		for (roll, version, release) in self.getRollNames(args, params):
                        if release:
                                rel = "rel='%s'" % release
                        else:
                                rel = 'rel=""'

			rows = self.db.execute("""
				select b.name from
				stacks s, rolls r, boxes b where
				r.name = '%s' and
				r.version = '%s' and %s and
				r.arch = '%s' and
				b.name = '%s' and
				s.box = b.id and s.roll=r.id
				""" % (roll, version, rel, arch, box))

			if not rows:
                                self.db.execute("""
					insert into stacks(box, roll)
                                        values (
                                        (select id from boxes where name='%s'),
                                        (select id from rolls where name='%s'
					and version='%s' and %s and arch='%s')
                                        )""" % (box, roll, version, rel, arch))

