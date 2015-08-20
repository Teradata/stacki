#
# Manipulate RedHat installer to include Rocks steps.
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
# Revision 1.10  2010/09/07 23:52:46  bruno
# star power for gb
#
# Revision 1.9  2009/05/01 19:06:48  mjk
# chimi con queso
#
# Revision 1.8  2008/10/18 00:55:45  mjk
# copyright 5.1
#
# Revision 1.7  2008/03/26 18:24:55  bruno
# another whack at ejecting the CD early
#
# Revision 1.6  2008/03/26 17:31:24  bruno
# eject the CD early
#
# Revision 1.5  2008/03/24 22:06:30  bruno
# eject the CD (if mounted) early in the install process
#
# Revision 1.4  2008/03/20 19:28:18  bruno
# first attempt at fixing frontend partitioning
#
# Revision 1.3  2008/03/06 23:41:30  mjk
# copyright storm on
#
# Revision 1.2  2007/12/17 22:23:00  bruno
# polish
#
# Revision 1.1  2007/12/10 21:28:33  bruno
# the base roll now contains several elements from the HPC roll, thus
# making the HPC roll optional.
#
# this also includes changes to help build and configure VMs for V.
#
#
from installclass import BaseInstallClass
from constants import *
from product import *
from flags import flags
import os, types
import iutil

import gettext
_ = lambda x: gettext.ldgettext("anaconda", x)

import installmethod
import yuminstall

import rpmUtils.arch

class InstallClass(BaseInstallClass):
	id = "stack"
	name = N_("Stack")
	sortPriority = 20000
	#hidden = 1
	hidden = 0

	def setSteps(self, anaconda):
		BaseInstallClass.setSteps(self, anaconda)

		os.system('touch /tmp/in-setSteps')

		if os.path.exists('/tmp/stack-skip-welcome'):
			anaconda.dispatch.skipStep("welcome", skip = 1)
		else:
			anaconda.dispatch.skipStep("welcome", skip = 0)

		#
		# skip the following 'graphical' screens
		#
		anaconda.dispatch.skipStep("parttype", skip = 1)
		anaconda.dispatch.skipStep("filtertype", skip = 1)
		anaconda.dispatch.skipStep("cleardiskssel", skip = 1)
		anaconda.dispatch.skipStep("bootloader", permanent = 1)
		anaconda.dispatch.skipStep("timezone", permanent = 1)
		anaconda.dispatch.skipStep("accounts", permanent = 1)
		anaconda.dispatch.skipStep("tasksel", permanent = 1)

		if os.path.exists('/tmp/manual-partitioning'):
			anaconda.dispatch.skipStep("partition", skip = 0)
			anaconda.dispatch.skipStep("autopartitionexecute",
				skip = 1)
		else:
			anaconda.dispatch.skipStep("partition", skip = 1)
			anaconda.dispatch.skipStep("autopartitionexecute",
				skip = 0)

		anaconda.dispatch.skipStep("group-selection", permanent = 1)
		anaconda.dispatch.skipStep("complete", permanent = 1)


	def getBackend(self):
		return yuminstall.YumBackend


	def __init__(self):
		BaseInstallClass.__init__(self)

