#! /opt/stack/bin/python
#
# @SI_Copyright@
#                             www.stacki.com
#                                  v3.0
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


class Nodes:
	"""A class that knows how to insert/delete rocks appliances from
	the cluster database"""

	def __init__(self, sql):
		# An open connection to the cluster database. (a stack.sql.App)
		self.sql = sql
		self.nodeid = -1

	def getNodeId(self):
		"Returns the id of the last node inserted"
		return self.nodeid
		
	def insert(self, name, mid, rack, rank, mac=None, ip=None,
			netmask=None, subnet='private'):

		"""Inserts a new node into the database. Optionally inserts
		networking information as well."""

		self.checkName(name)
		self.checkMembership(mid)
		self.checkMAC(mac)
		self.checkIP(ip)
		self.checkSubnet(subnet)
		
		self.sql.execute("""
			insert into nodes (name, appliance, rack, rank)
			values ("%s", %d, %d, %d)
			""" % (name, mid, rack, rank))

		# The last insert id.
		nodeid = self.sql.insertId()

		# Do not go further if there is no networking info.
		if ip is None:
			return

		#
		# now create a new row in the networks table
		#
		# First get the subnet you want to insert the node into. The
		# default is "private", but this should be dynamic enough
		# to accept any kind of string that is valid

		self.sql.execute("select id from subnets where name='%s'"
								% (subnet))
		subnet_id = int(self.sql.fetchone()[0])
		
		if mac is None:
			# Happens for a frontend
			insert = ('insert into networks '
				'(node,ip,netmask,name,subnet) '
				'values (%d, "%s", "%s", "%s", %d) '
				% (nodeid, ip, netmask, name, subnet_id))
		else:
			insert = ('insert into networks '
				'(node,mac,ip,netmask,name,subnet) '
				'values (%d, "%s", "%s", "%s", "%s", %d) '
				% (nodeid, mac, ip, netmask, name, subnet_id))

		self.sql.execute(insert)
		self.nodeid = nodeid
		

	def checkName(self, checkname):
		"Check to make sure we don't insert a duplicate node name"

		host = self.sql.getNodeId(checkname)
		if host:
			msg = 'Node %s already exists.\n' % checkname 
			msg += 'Select a different hostname, cabinet '
			msg += 'and/or rank value.'
			raise ValueError, msg

	def checkSubnet(self,subnet):
		"Check to see if the subnet exists"

		rows = self.sql.execute("select id from subnets where name='%s'" % subnet);
		if (rows == 0):
			msg = "subnet %s does not exist. Bailing out" % (subnet)
			raise KeyError, msg
			return

	def checkIP(self, ipaddr):
		"Check if the address is already in the database"
		
		if ipaddr is None:
			return
		
		nodeid = self.sql.getNodeId(ipaddr)

		if nodeid:
			msg = "Duplicate IP '%s' Specified" % ipaddr
			raise ValueError, msg


	def checkMAC(self, mac):
		"""Mac addresses are unique accross all sites."""

		#
		# check if mac is already in the database
		# Special Handling for literal "None"

		if mac is None:
			return

		query = 'select mac from networks where mac = "%s"' % mac

		if self.sql.execute(query) == 1:
			msg = "Duplicate MAC '%s' Specified" % mac
			raise ValueError, msg


	def checkMembershipName(self, name):

		query='select membership from appliances where membership="%s" ' % (name)
		
		if self.sql.execute(query) == 0:
			msg = 'Could not find Membership "%s"' % name
			raise ValueError, msg


	def checkMembership(self, mid):
		query='select id from appliances where id="%s"' % mid
		if self.sql.execute(query) == 0:
			msg = 'Invalid Membership ID "%s"' % mid
			raise ValueError, msg
