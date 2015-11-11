#
# $Id: welcome_gui.py,v 1.15 2010/09/07 23:52:46 bruno Exp $
#
# Our patch to redhat's installer
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
# $Log: welcome_gui.py,v $
# Revision 1.15  2010/09/07 23:52:46  bruno
# star power for gb
#
# Revision 1.14  2009/10/07 00:02:38  bruno
# new path to firefox
#
# Revision 1.13  2009/06/02 00:54:57  bruno
# suppress an error message when building frontends
#
# Revision 1.12  2009/05/01 19:06:48  mjk
# chimi con queso
#
# Revision 1.11  2009/03/21 22:22:55  bruno
#  - lights-out install of VM frontends with new node_rolls table
#  - nuked 'site' columns and tables from database
#  - worked through some bugs regarding entities
#
# Revision 1.10  2009/03/04 01:32:12  bruno
# attributes work for frontend installs
#
# Revision 1.9  2008/10/18 00:55:45  mjk
# copyright 5.1
#
# Revision 1.8  2008/07/18 20:49:07  bruno
# now have ability to build any appliance from rocks 'boot:' prompt. just
# type 'bulid appliance=xml-node-name', for example:
# 'build appliance=vm-container-sever'
#
# change 'boot:' directive of 'frontend' to 'build'
#
# Revision 1.7  2008/05/22 21:02:06  bruno
# rocks-dist is dead!
#
# moved default location of distro from /export/home/install to
# /export/rocks/install
#
# Revision 1.6  2008/03/26 19:48:18  bruno
# forgot to remove all references to 'media'
#
# Revision 1.5  2008/03/26 18:24:55  bruno
# another whack at ejecting the CD early
#
# Revision 1.4  2008/03/26 17:31:24  bruno
# eject the CD early
#
# Revision 1.3  2008/03/24 22:06:30  bruno
# eject the CD (if mounted) early in the install process
#
# Revision 1.2  2008/03/06 23:41:30  mjk
# copyright storm on
#
# Revision 1.1  2007/12/10 21:28:32  bruno
# the base roll now contains several elements from the HPC roll, thus
# making the HPC roll optional.
#
# this also includes changes to help build and configure VMs for V.
#
# Revision 1.12  2006/12/04 22:05:48  bruno
# lights-out tweak
#
# Revision 1.11  2006/11/29 23:12:40  bruno
# prototype support for lights out frontend installs
#
# Revision 1.10  2006/09/11 22:47:01  mjk
# monkey face copyright
#
# Revision 1.9  2006/08/10 00:09:25  mjk
# 4.2 copyright
#
# Revision 1.8  2006/06/22 22:13:27  bruno
# cleanup of installclass files
#
# Revision 1.7  2006/06/21 03:09:52  bruno
# updates to put the frontend networking info in the database just like
# a compute node
#
# Revision 1.6  2006/06/05 17:57:33  bruno
# first steps towards 4.2 beta
#
# Revision 1.5  2006/01/18 01:39:24  yuchan
# add code _ and rhpl.translate for supporting localization - yuchan
#
# Revision 1.4  2005/10/12 18:08:28  mjk
# final copyright for 4.1
#
# Revision 1.3  2005/09/16 01:02:08  mjk
# updated copyright
#
# Revision 1.2  2005/05/24 21:21:47  mjk
# update copyright, release is not any closer
#
# Revision 1.1  2005/03/01 00:22:52  mjk
# moved to base roll
#
# Revision 1.2  2004/03/25 03:15:43  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.1  2004/03/08 21:01:23  mjk
# *** empty log message ***
#
# Revision 1.6  2003/11/30 15:04:10  bruno
# removing redhat trademarks
#
# Revision 1.5  2003/09/24 17:08:45  fds
# Bruno's changes for RH 9
#
# Revision 1.4  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.3  2003/08/13 22:39:18  bruno
# added spaces to cleanup first line on install screen
#
# Revision 1.2  2003/05/22 16:36:23  mjk
# copyright
#
# Revision 1.1  2003/04/25 18:15:09  bruno
# first pass at adding all the new rocks config screens
#
#
#

#
# support for GUI installs
#
import gtk
import gui
import sys
from iw_gui import *

from constants import *
import gettext
_ = lambda x: gettext.ldgettext("anaconda", x)

import os
import string
import subprocess

import sys
sys.path.append('/opt/stack/lib/python2.6/site-packages')


class WelcomeWindow(InstallWindow):

	windowTitle = "" #N_("Welcome to stacki")

	def displayBrowser(self):
		bossenv = os.environ.copy()
		bossenv['LD_LIBRARY_PATH'] = \
			'/opt/stack/lib:/tmp/updates/usr/lib64'
		bossenv['DISPLAY'] = ':1'
		s = subprocess.Popen('/opt/stack/bin/boss_config.py',
			env = bossenv)
		s.wait()

		return


	def regenerateKickstartFile(self):
		bossenv = os.environ.copy()
		if 'LD_LIBRARY_PATH' in bossenv:
			bossenv['LD_LIBRARY_PATH'] = \
				'%s:/opt/stack/lib:/tmp/updates/lib64' \
				% bossenv['LD_LIBRARY_PATH']
		else:
			bossenv['LD_LIBRARY_PATH'] = \
				'/opt/stack/lib:/tmp/updates/lib64'

		s = subprocess.Popen('/opt/stack/bin/boss_ks_file.py',
			env = bossenv)
		s.wait()

		return


	def __init__ (self, ics):
		InstallWindow.__init__(self, ics)
		ics.setGrabNext(1)
		self.anaconda = None

		if not os.path.exists('/tmp/site.attrs'):
			#
			# run the browser to select the rolls and
			# to build the /tmp/site.attrs file
			#
			self.displayBrowser()

		#
		# this will ensure that this screen is *not* called
		# again when anaconda is restarted
		#
		file = open('/tmp/stack-skip-welcome', 'w')
		file.close()

		self.regenerateKickstartFile()

		#
		# after rebuilding the kickstart file, stop this
		# version of anaconda and let the anaconda script restart it
		#
		s = subprocess.Popen([ '/usr/bin/killall', 'Xorg' ])
		s.wait()

		sys.exit(0)

