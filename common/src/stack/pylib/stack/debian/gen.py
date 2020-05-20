#! /opt/stack/bin/python
# 
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import sys
from stack.bool import str2bool
import stack.gen

apt_template = """apt install -y %s
[ $? -ne 0 ] && echo "Package Installation Failed. Cannot Continue" && exit -1
"""

class BashProfileTraversor(stack.gen.MainTraversor):

	def shellPackages(self, enabled, disabled):
		if enabled:
			return apt_template % ' '.join(pkg.lower() for pkg in enabled)
		
		return None
		
		
class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)
		self.nativeSection	 = stack.gen.ProfileSection()
		self.scriptSection	 = stack.gen.ProfileSection()

		# We could set these elsewhere but this is the current
		# definition of the RedHat Generator.
		#
		# We used to do i386 (not anymore)

#		self.setOS('redhat')
#		self.setArch('x86_64')

	def traversors(self):
		profileType = self.getProfileType()
		workers     = [ ]

		if profileType == 'native':
			print('error - native profile not implemented')
			sys.exit(-1)
		elif profileType == 'bash':
			workers.extend([ BashProfileTraversor(self) ])
		elif profileType == 'ansible':
			workers.extend([ stack.gen.AnsibleProfileTraversor(self) ])

		return workers




