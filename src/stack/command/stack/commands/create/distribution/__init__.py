# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
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
import os.path
import tempfile
import shutil
import stack
import stack.commands
import stack.dist
import stack.build
from stack.exception import *

class Command(stack.commands.create.command,
	      stack.commands.DistributionArgumentProcessor):
	"""
	Create a Stack distribution. This distribution is used to install
	Stack nodes.

	<arg type='string' name='distribution'>
	The name of the distribution to build. Use "stack list distribution"
	to get the list of all valid distributions.
	Default is "default".
	</arg>

	<param type='bool' name='inplace'>
	If true, then build the distribution in the current directory.
	Default is false.
	</param>

        <param type='bool' name='resolve'>
        If true, then resolve RPM versions during the build so only the
        most recent is included in the distribution. Normally this is
        not required since yum and anaconda expect all versions to be
        present. Currently, this option exists for internal use only.
	Default is false.
	</param>

	<param type='bool' name='md5'>
	If true, then calculate the MD5 checksums for all files in the
	distribution.
	Default is true.
	</param>

	<param type='string' name='root'>
	The root directory where the pallets are located.
	Default is "/export/stack".
	</param>

	<param type='string' name='pallets'>
	A space separated list of pallets to use when building a distribution.
	"name,version" is required when delimiting pallets.
	
	For example: pallets="stacki,1.0 os,6.6". Default is "None".
	</param>

	<example cmd='create distribution'>
	Create a RedHat distribution in /export/stack/distributions/default.
	</example>

	<related>list distribution</related>
	<related>remove distribution</related>
	"""

	def getCarts(self, dist):
		"""
		Get a list of carts used to build this distribution
		"""

		carts = []
		self.db.execute("""
			select c.name from
			cart_stacks s, distributions d, carts c where
			s.distribution = d.id and s.cart = c.id and
			d.name='%s'
			""" % dist)
		for name,  in self.db.fetchall():
			carts.append(name)

		return carts
        
	def getRolls(self, dist):
		"""
		Get a list of pallets used to build this distribution
		"""

		rolls = []
		self.db.execute("""
			select r.name, r.version from
			stacks s, distributions d, rolls r where
			s.distribution = d.id and s.roll = r.id and
			d.name='%s'
			""" % dist)
		for name, version in self.db.fetchall():
			rolls.append([name, version, True])

		return rolls


	def run(self, params, args):

		if not args:		# default is just build default
			args = [ 'default' ]

		(inplace, resolve, md5, root, withrolls)  = self.fillParams([
			('inplace', 'n'),
			('resolve', 'n'),
			('md5', 'y'),
			('root', '/export/stack'),
			('pallets', None),
			])


		inplace = self.str2bool(inplace)
		resolve = self.str2bool(resolve)
		md5     = self.str2bool(md5)
		rolls   = []
		if withrolls:
			for i in withrolls.split(' '):
				rolls.append(i.split(',') + [ True ] )

		if rolls and len(args) != 1:
			raise CommandError(self, 'pallets option requires exactly one distribution')

		if not self.db or rolls:
			if len(args) != 1:
				# No DB -- FE Kickstart Env
                                raise CommandError(self, 'must supply exactly one distribution')
			distributions = args
		else:
			distributions = self.getDistributionNames(args)

		for distName in distributions:
			if self.db and not withrolls:
				rolls = self.getRolls(distName)
				self.db.execute("""
					select os from distributions d where
					d.name='%s'
					""" % distName)
				distOS, = self.db.fetchone()
			else:
				distOS = 'redhat'

			lockfile = '/var/lock/%s' % distName
			if os.path.exists(lockfile):
                                raise CommandError(self,
					"Lockfile %s exists.\n" % lockfile +
					"Another instance of stack create " +
					"distribution is running")
			os.system('touch %s' % lockfile)

                        carts = self.getCarts(distName)
                        
			print 'Building %s distribution' % distName

			self.runImplementation(distOS,
					       [ distName,
						 inplace,
						 resolve,
						 md5,
						 root,
						 rolls,
                                                 carts ])

			if not inplace:
				#
				# after the distribution building completes,
				# increment its version number
				#
				attr = 'distribution.%s/version' % distName
				dist_version = self.db.getHostAttr('localhost',
					attr)

				if dist_version:
					try:
						dist_version = \
							int(dist_version) + 1
					except:
						dist_version = 1
				else:
					dist_version = 1

				self.command('set.attr', [ 'attr=%s' % attr,
					'value=%s' % dist_version ])

				print 'Distribution version: ', dist_version
					
			os.unlink(lockfile)

