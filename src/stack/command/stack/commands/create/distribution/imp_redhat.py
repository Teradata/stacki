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

class Implementation(stack.commands.Implementation):

	def run(self, args):
		(dist, inplace, resolve, md5, root, rolls) = args

		if not inplace:
			path = os.path.join(root, 'distributions')
			if not os.path.exists(path):
				os.makedirs(path)
				os.system('chmod 755 %s' % path)
			os.chdir(path)

		mirror = stack.dist.Mirror()
		mirror.setHost('rolls')
		mirror.setPath(root)
		mirror.setRoot(root)
		mirror.setArch(self.owner.arch)

		mirrors = []
		mirrors.append(mirror)

		distro = stack.dist.Distribution(mirrors, stack.version)
		distro.setRoot(os.getcwd())


		#
		# build the new distro in a temporary directory
		#
		tempdist = tempfile.mkdtemp(dir='')
		distro.setDist(tempdist)

		distro.setLocal('/usr/src/redhat')
		distro.setContrib(os.path.join(mirror.getRootPath(),
			'contrib', dist, stack.version))
		distro.setSiteProfiles(os.path.join(mirror.getRootPath(),
			'site-profiles', dist, stack.version))


		#
		# build it
		# 
		builder = stack.build.DistributionBuilder(distro)

		builder.setResolveVersions(resolve)
		builder.setRolls(rolls)
		builder.setSiteProfiles(True)
		builder.setMD5(md5)
		builder.build()

		#
		# make sure everyone can traverse the the rolls directories
		#
		mirrors = distro.getMirrors()
		fullmirror = mirrors[0].getRollsPath()
		os.system('find %s -type d ' % (fullmirror) + \
			  '-exec chmod -R 0755 {} \;')


		#
		# now move the previous distro into a temporary
		# directory
		#
		prevdist = tempfile.mkdtemp(dir='')
		try:
			shutil.move(dist, prevdist)
		except:
			pass


		#
		# rename the temporary distro (the one we just built)
		# to the 'official' name and make sure the permissions
		# are correct
		#
		shutil.move(tempdist, dist)
		os.system('chmod 755 %s' % dist)

		if not inplace:
			#
			# if this is the repo that is associated with the
			# frontend, then recreate the yum package metadata
			# and cache
			#
			fedist = None
			output = self.owner.call('list.host', [ 'localhost' ])
			for o in output:
				fedist = o['distribution']

			if dist == fedist:
				os.system('yum clean --disablerepo=* ' +
					'--enablerepo=stacki-%s ' % stack.version +
					'all')
				os.system('yum makecache --disablerepo=* ' +
					'--enablerepo=stacki-%s ' % stack.version +
					'all')
			#
			# restart the tracker because we don't want packages
			# from the previous distro to be tracked
			#
			os.system('/sbin/service stack-tracker restart')

		#
		# nuke the previous distro
		#
		try:
			shutil.rmtree(prevdist)
		except:
			pass
		
