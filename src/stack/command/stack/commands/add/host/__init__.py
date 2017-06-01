# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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
import re
import sys
import string
import socket
import stack.commands
from stack.exception import *

class command(stack.commands.HostArgumentProcessor,
              stack.commands.ApplianceArgumentProcessor,
              stack.commands.BoxArgumentProcessor,
              stack.commands.EnvironmentArgumentProcessor,
              stack.commands.add.command):
	pass
	
class Command(command):
	"""
	Add an new host to the cluster.

        <arg type='string' name='host'>
        A single host name.  If the hostname is of the standard form of
	basename-rack-rank the default values for the appliance, rack,
	and rank parameters are taken from the hostname.
        </arg>

	<param type='string' name='longname'>
	Long appliance name.  If not provided and the host name is of
	the standard form the long name is taken from the basename of 
	the host.
	</param>

        <param type='string' name='rack'>
        The number of the rack where the machine is located. The convention
	in Stacki is to start numbering at 0. If not provided and the host
	name is of the standard form the rack number is taken from the host
	name.
        </param>

	<param type='string' name='rank'>
	The position of the machine in the rack. The convention in Stacki
	is to number from the bottom of the rack to the top starting at 0.
	If not provided and the host name is of the standard form the rank
	number is taken from the host name.
	</param>

	<param type='string' name='box'>
	The box name for the host. The default is: "default".
	</param>

        <param type='string' name='environment'>
        Name of the host environment.  For most users this is not specified.
        Environments allow you to partition hosts into logical groups.
	</param>

	<example cmd='add host backend-0-1'>
	Adds the host "backend-0-1" to the database with 1 CPU, a appliance
	name of "backend", a rack number of 0, and rank of 1.
	</example>

	<example cmd='add host backend rack=0 rank=1 longname=Backend'>
	Adds the host "backend" to the database with 1 CPU, a long appliance name
	of "Backend", a rack number of 0, and rank of 1.
	</example>

	<related>add host interface</related>

	"""

	def addHost(self, host):
                
		if host in self.getHostnames():
			raise CommandError(self, 'host "%s" already exists in the database' % host)
	
		# If the name is of the form appliancename-rack-rank
		# then do the right thing and figure out the default
		# values for appliane, rack, and rank.  If the appliance 
		# name is not found in the database, or the rack/rank numbers
		# are invalid do not guess any defaults.  The name is
		# either 100% used or 0% used.
	
		appliances = self.getApplianceNames()

		appliance = None
		rack = None
		rank = None

		try:
			basename, rack, rank = host.split('-')
			if basename in appliances:
				appliance = basename
				rack = (rack)
				rank = (rank)
		except:
			appliance = None
			rack = None
			rank = None
				
		# fillParams with the above default values
		(appliance, longname, rack, rank, box, environment,
			osaction, installaction) = \
			self.fillParams( [
				('appliance', appliance),
				('longname', None),
				('rack', rack),
				('rank', rank),
				('box', 'default'),
                                ('environment', ''),
				('osaction','default'),
				('installaction','default') ])

		if not longname and not appliance:
                        raise ParamRequired(self, ('longname', 'appliance'))

		if rack == None:
                        raise ParamRequired(self, 'rack')
		if rank == None:
                        raise ParamRequired(self, 'rank')

		if longname and not appliance:
			#
			# look up the appliance name
			#
			for o in self.call('list.appliance'):
				if o['long name'] == longname:
					appliance = o['appliance']
					break

			if not appliance:
                        	raise CommandError(self, 'longname "%s" is not in the database' % longname)

		if appliance not in appliances:
			raise CommandError(self, 'appliance "%s" is not in the database' % appliance)

		if box not in self.getBoxNames():
			raise CommandError(self, 'box "%s" is not in the database' % box)

		# Get IDs for OS and Box
		boxid, osid = self.db.select("id, os from boxes where name='%s'" % box)[0]
		boxid = int(boxid)
		osid = int(osid)

		# Get Bootname ID matched against a triple of (bootname, boottype, OS)
		ia = self.db.select("""b.id from bootnames b, bootactions ba 
			where b.name="%s" and b.type="install" and b.id=ba.bootname
			and ba.os=%d""" %
			(installaction, osid))
		# If we can't find one, try to get one where OS is set to 0, ie.
		# common action for all OSes
		if not ia:
			ia = self.db.select("""b.id from bootnames b, bootactions ba 
				where b.name="%s" and b.type="install" and b.id=ba.bootname
				and ba.os=0"""
				% installaction)

		# If we cannot find an install action to map to, bail out
		if not ia:
			(osname,) = self.db.select("name from oses where id=%d" % osid)[0]
			raise CommandError(self, "Cannot find %s install action for OS %s" % 
				(installaction, osname))
		installaction_id = int(ia[0][0])

		# Same logic as above. This time try to get bootaction where
		# boottype is "OS"
		oa = self.db.select("""b.id from bootnames b, bootactions ba 
			where b.name="%s" and b.type="os" and b.id=ba.bootname
			and ba.os=%d""" % 
			(osaction, osid))
		if not oa:
			oa = self.db.select("""b.id from bootnames b, bootactions ba 
				where b.name="%s" and b.type="os" and b.id=ba.bootname
				and ba.os=0""" % osaction)
		# If we cannot find an os action to map to, bail out
		if not oa:
			(osname,) = self.db.select("name from oses where id=%d" % osid)[0]
			raise CommandError(self, "Cannot find %s os action for OS %s" % 
				(osaction, osname))

		osaction_id = int(oa[0][0])
				
		self.db.execute("""insert into nodes
			(name, appliance, box, rack, rank, osaction, installaction)
                        values ('%s', (select id from appliances where name='%s'),
			%d, '%s', '%s', %d, %d) """ %
                        (host, appliance, boxid, rack, rank, osaction_id, installaction_id))

                if environment:
                        self.command('set.host.environment', [ host, environment ])
                        

	def run(self, params, args):
		if len(args) != 1:
                        raise ArgUnique(self, 'host')

		host = args[0]
		self.addHost(host)
