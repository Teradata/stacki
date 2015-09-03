#!/opt/stack/bin/python
#
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
import shlex
import subprocess
import json
import syslog
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

		ipaddr = None
		if os.environ.has_key('REMOTE_ADDR'):
                	ipaddr = os.environ['REMOTE_ADDR']
                if not ipaddr:
                        return

        	syslog.syslog(syslog.LOG_INFO, 'remote addr %s' % ipaddr)
                
		if os.environ.has_key('HTTP_X_STACK_PARTITIONINFO'):

			partinfo = os.environ['HTTP_X_STACK_PARTITIONINFO']
                        try:
				partinfo = json.loads(partinfo)
                        except:
                                syslog.syslog(syslog.LOG_ERR, 'invalid partinfo %s' % partinfo)
                                partinfo = None

                        if partinfo:
#                                syslog.syslog(syslog.LOG_INFO, 'partinfo %s' % partinfo)
                                
                                p = subprocess.Popen( [ '/opt/stack/bin/stack',
                                                        'remove',
                                                        'host',
                                                        'partition',
                                                        ipaddr ], stdout=None, stderr=None)
                                rc = p.wait()

                                self.connect()

                                inserts = []
                                for disk in partinfo.keys():
                                        for part in partinfo[disk]:
                                                inserts.append(self.setPartitionInfo(ipaddr, part))

                                for insert in inserts:
                                        self.execute(insert)

                                self.close()

                # The following attributes are one shot booleans and
                # should always be reset even if the partinfo was corrupt.
                
		os.system('/opt/stack/bin/stack set host attr %s attr=nukedisks value=false' % ipaddr)
		os.system('/opt/stack/bin/stack set host attr %s attr=nukecontroller value=false' % ipaddr)
                
		print 'Content-type: application/octet-stream'
		print 'Content-length: %d' % (len(''))
		print ''
		print ''

		return

syslog.openlog('setDbPartitions.cgi', syslog.LOG_PID, syslog.LOG_LOCAL0)
app = App()
app.run()
syslog.closelog()
