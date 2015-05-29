#!/opt/stack/bin/python
#
# $Id$
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
# Revision 1.16  2010/09/07 23:53:07  bruno
# star power for gb
#
# Revision 1.15  2009/05/01 19:07:07  mjk
# chimi con queso
#
# Revision 1.14  2008/10/18 00:56:01  mjk
# copyright 5.1
#
# Revision 1.13  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.12  2007/12/10 21:28:35  bruno
# the base roll now contains several elements from the HPC roll, thus
# making the HPC roll optional.
#
# this also includes changes to help build and configure VMs for V.
#
# Revision 1.11  2007/06/23 04:03:23  mjk
# mars hill copyright
#
# Revision 1.10  2006/09/11 22:47:17  mjk
# monkey face copyright
#
# Revision 1.9  2006/08/10 00:09:38  mjk
# 4.2 copyright
#
# Revision 1.8  2006/01/16 06:48:59  mjk
# fix python path for source built foundation python
#
# Revision 1.7  2005/10/12 18:08:40  mjk
# final copyright for 4.1
#
# Revision 1.6  2005/09/16 01:02:19  mjk
# updated copyright
#
# Revision 1.5  2005/09/13 19:26:21  bruno
# move to foundation
#
# Revision 1.4  2005/05/24 21:21:55  mjk
# update copyright, release is not any closer
#
# Revision 1.3  2005/05/23 23:59:24  fds
# Frontend Restore
#
# Revision 1.2  2005/04/28 21:47:24  bruno
# partitioning function updates in order to support itanium.
#
# itanics need 'parted' as 'sfdisk' only looks at block 0 on a disk and
# itanics put their real partition info in block 1 (this is the GPT partitioning
# scheme)
#
# Revision 1.1  2005/03/01 02:02:49  mjk
# moved from core to base
#
# Revision 1.1  2005/02/14 21:53:04  bruno
# added setDbPartitions.cgi for phil's phartitioning phun
#
#
#

import os
import shlex
import subprocess
import stack.sql

class App(stack.sql.Application):

	def __init__(self):
		stack.sql.Application.__init__(self)
		self.response = ''


	def setPartitionInfo(self, host, part):
		columns = []
		values = []

		columns.append('node')
		values.append('%s' % self.getNodeId(host))

		(dev,sect,size,id,fstype,fflags,pflags,mnt,uuid) = part

		if dev:
			columns.append('device')
			values.append('"%s"' % dev)
		if sect:
			columns.append('sectorstart')
			values.append('"%s"' % sect)
		if size:
			columns.append('partitionsize')
			values.append('"%s"' % size)
		if id:
			columns.append('partitionid')
			values.append('"%s"' % id)
		if fstype:
			columns.append('fstype')
			values.append('"%s"' % fstype)
		if fflags:
			columns.append('formatflags')
			values.append('"%s"' % fflags)
		if pflags:
			columns.append('partitionflags')
			values.append('"%s"' % pflags)
		if mnt:
			columns.append('mountpoint')
			values.append('"%s"' % mnt)
		if uuid:
			columns.append('uuid')
			values.append('"%s"' % uuid)

		insert = 'insert into partitions (%s) values (%s);' % \
			(','.join(columns), ','.join(values))

		return insert


        def run(self):

		host = ''
		if os.environ.has_key('REMOTE_ADDR'):
                	host = os.environ['REMOTE_ADDR']

		if os.environ.has_key('HTTP_X_STACK_PARTITIONINFO'):
			partinfo = \
				eval(os.environ['HTTP_X_STACK_PARTITIONINFO'])

			cmd = """/opt/stack/bin/stack remove host partition
				%s""" % host
			c = shlex.split(cmd)
			p = subprocess.Popen(c, stdout=None, stderr=None)
			rc = p.wait()

			self.connect()

			inserts = []
			for disk in partinfo.keys():
				for part in partinfo[disk]:
					inserts.append(self.setPartitionInfo(host, part))

			for insert in inserts:
				self.execute(insert)

			self.close()

		os.system('/opt/stack/bin/stack set host attr ' +\
			'%s attr=nukedisks value=false' % host)
		os.system('/opt/stack/bin/stack set host attr ' +\
			'%s attr=nukecontroller value=false' % host)
		print 'Content-type: application/octet-stream'
		print 'Content-length: %d' % (len(''))
		print ''
		print ''

		return

app = App()
app.run()

