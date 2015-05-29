#! /opt/stack/bin/python
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
# Revision 1.14  2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.13  2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.12  2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.11  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.10  2007/06/23 04:03:24  mjk
# mars hill copyright
#
# Revision 1.9  2006/09/11 22:47:23  mjk
# monkey face copyright
#
# Revision 1.8  2006/08/10 00:09:41  mjk
# 4.2 copyright
#
# Revision 1.7  2006/01/16 06:49:00  mjk
# fix python path for source built foundation python
#
# Revision 1.6  2005/10/12 18:08:42  mjk
# final copyright for 4.1
#
# Revision 1.5  2005/09/16 01:02:21  mjk
# updated copyright
#
# Revision 1.4  2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.3  2005/05/24 21:21:57  mjk
# update copyright, release is not any closer
#
# Revision 1.2  2005/03/15 07:07:22  bruno
# AMD64 is dead -- long live x86_64
#
# Revision 1.1  2005/03/01 00:22:08  mjk
# moved to base roll
#
# Revision 1.22  2005/02/07 18:13:04  mjk
# removed dead code (predates the graph)
#
# Revision 1.21  2004/09/14 19:47:38  bruno
# pretty close to making a working CD
#
# Revision 1.20  2004/09/13 23:15:03  bruno
# update the path to kickstart.cgi to include 'sbin'
#
# Revision 1.19  2004/03/25 03:15:48  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.18  2003/10/17 23:46:31  mjk
# Where is Yamhill
#
# Revision 1.17  2003/10/15 22:18:21  bruno
# now can build a bootable taroon-based CD that installs on a frontend
#
# Revision 1.16  2003/09/24 17:08:45  fds
# Bruno's changes for RH 9
#
# Revision 1.15  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.14  2003/05/22 16:39:28  mjk
# copyright
#
# Revision 1.13  2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.12  2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.11  2002/07/10 18:54:03  bruno
# changes to make 7.3 installation from CD work
#
# Revision 1.10  2002/02/26 01:12:52  mjk
# - Remove more of the --cdrom stuff from bruno, thanks to my screwup
# - Added audiofile rpm back the x11 config (gnome needs sound, piece of crap)
# - Burned down a frontend and compute nodes looks pretty good.
#
# Revision 1.9  2002/02/23 00:10:46  bruno
# updates to handle 'negative' packages. the cdrom builder needs them and
# kickstarting nodes don't.
#
# Revision 1.8  2002/02/21 21:33:28  bruno
# added new copyright
#
# Revision 1.7  2001/11/09 00:19:02  mjk
# ia64 changes
#
# Revision 1.5  2001/10/30 02:17:54  mjk
# - Were cooking with CGI kickstart now
# - added popen stuff to ks.py
# - verify command is dead
#
# Revision 1.4  2001/09/10 18:31:12  mjk
# wish I remembered what changed...
#
# Revision 1.3  2001/06/29 23:38:58  mjk
# Added Python Kickstart support
#
# Revision 1.2  2001/05/09 20:17:22  bruno
# bumped copyright 2.1
#
# Revision 1.1  2001/05/04 22:58:53  mjk
# - Added 'cdrom' command, and CDBuilder class.
# - CDBuilder uses RedHat's source to parse the hdlist/comps file so we can
#   trim the set of RPMs on our CD.
# - Weekend!
#

import os
import string
import re
import stack.file

class KickstartFile:

    def __init__(self, file, arch, distdir=None):
        self.dict	= {}
        key		= 'main'
        val		= []
        self.raw	= []

        cmd = './sbin/kickstart.cgi --arch=%s --membership=%s' % (arch, file)

        if (distdir):
            cmd = cmd + ' --dist=%s' % (distdir)

        for line in os.popen(cmd).readlines() :
            self.raw.append(line)
            s = string.split(line[:-1], '#')[0]
            if s:
                if s[0] == '%':
                    key = string.split(s[1:])[0]
                    val = []
                else:
                    if not self.dict.has_key(key):
                        self.dict[key] = [s]
                    else:
                        self.dict[key].append(s)
        
    def getSection(self, name):
        if self.dict.has_key(name):
            return self.dict[name]
        else:
            return None

    def getRaw(self):
	return self.raw


