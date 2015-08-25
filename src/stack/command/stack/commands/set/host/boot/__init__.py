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

import sys
import string
import stack.commands
import os
from stack.exception import *

class Command(stack.commands.set.host.command):
	"""
	Set a bootaction for a host. A hosts action can be set to 'install' 
	or to 'os' (also, 'run' is a synonym for 'os').

	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='action'>
	The label name for the bootaction. This must be one of: 'os',
	'install', or 'run'.

	If no action is supplied, then only the configuration file for the
	list of hosts will be rewritten.
	</param>
		
	<example cmd='set host boot compute-0-0 action=os'>
	On the next boot, compute-0-0 will boot the profile based on its
	"run action". To see the node's "run action", execute:
	"rocks list host compute-0-0" and examine the value in the
	"RUNACTION" column.
	</example>
	"""

	def writeDefaultPxebootCfg(self):
		nrows = self.db.execute("""
                	select kernel, ramdisk, args from
			bootaction where action='install'
                        """)

		if nrows == 1:
			kernel, ramdisk, args = self.db.fetchone()

			filename = '/tftpboot/pxelinux/pxelinux.cfg/default'
			file = open(filename, 'w')
			file.write('default stack\n')
			file.write('prompt 0\n')
			file.write('label stack\n')

			if len(kernel) > 6 and kernel[0:7] == 'vmlinuz':
				file.write('\tkernel %s\n' % (kernel))
			if len(ramdisk) > 0:
				if len(args) > 0:
					args += ' initrd=%s' % ramdisk
				else:
					args = 'initrd=%s' % ramdisk
			if len(args) > 0:
				file.write('\tappend %s\n' % (args))

			# If using ksdevice=bootif we need to
			# pass the PXE information to loader.
			
			if args and args.find('bootif') != -1:
				file.write('\tipappend 2\n')

			file.close()

			#
			# make sure apache can update the file
			#
			os.system('chown root.apache %s' % (filename))
			os.system('chmod 664 %s' % (filename))


	def writeFile(self, host, action, filename, ip, netmask, gateway):
		# Get the bootaction for the host (install or os) and
		# lookup the actual kernel, ramdisk, and args for the
		# specific action.

		for row in self.call('list.host', [ host ]):
			if action == 'install':
				bootaction = row['installaction']
			else:
				bootaction = row['runaction']

		kernel = ramdisk = args = None
		for row in self.call('list.bootaction'):
			if row['action'] == bootaction:
				kernel  = row['kernel']
				ramdisk = row['ramdisk']
				args    = row['args']

		if not kernel:
			print 'bootaction "%s" for host "%s" is invalid' % \
				(action, host)
			sys.exit(-1)

		# If the ksdevice= is set fill in the network
		# information as well.  This will avoid the DHCP
		# request inside anaconda.

		if args and args.find('ksdevice=') != -1:
			dnsserver = self.db.getHostAttr(host,
				'Kickstart_PrivateDNSServers')
			nextserver = self.db.getHostAttr(host,
				'Kickstart_PrivateKickstartHost')
			
			args += ' ip=%s gateway=%s netmask=%s dns=%s nextserver=%s' % \
				(ip, gateway, netmask, dnsserver, nextserver)

		if filename != None:
			file = open(filename, 'w')	
			file.write('default stack\n')
			file.write('prompt 0\n')
			file.write('label stack\n')

			if kernel:
				if kernel[0:7] == 'vmlinuz':
					file.write('\tkernel %s\n' % (kernel))
				else:
					file.write('\t%s\n' % (kernel))
			if ramdisk and len(ramdisk) > 0:
				if len(args) > 0:
					args += ' initrd=%s' % ramdisk
				else:
					args = 'initrd=%s' % ramdisk

			if args and len(args) > 0:
				file.write('\tappend %s\n' % (args))

			# If using ksdevice=bootif we need to
			# pass the PXE information to loader.
			
			if args and args.find('bootif') != -1:
				file.write('\tipappend 2\n')

			file.close()

			#
			# make sure apache can update the file
			#
			import pwd
			import grp

                        uid = pwd.getpwnam('root').pw_uid
			gid = grp.getgrnam('apache').gr_gid
                        try:
                                os.chown(filename, uid, gid)
                        except OSError:
                                pass
                        try:
				os.chmod(filename, 0664)
                        except OSError:
                                pass


	def writePxebootCfg(self, host, action):
		#
		# Get the IP and NETMASK of the host
		#
		for row in self.call('list.host.interface',
				[ host, 'expanded=true' ]):

			ip = row['ip']
			if ip:
				#
				# Compute the HEX IP filename for the host
				#
				filename = '/tftpboot/pxelinux/pxelinux.cfg/'
				hexstr = ''
				for i in string.split(ip, '.'):
					hexstr += '%02x' % (int(i))
				filename += '%s' % hexstr.upper()

				if row['pxe']:
					self.writeFile(host, action, filename,
						ip, row['mask'], row['gateway'])
				else:
					#
					# if present, remove the old PXE
					# config file
					#
					if os.path.exists(filename):
						os.unlink(filename)

	def updateBoot(self, host, action):
		#
		# is there already an entry in the boot table
		#
		nrows = self.db.execute("""select b.id from boot b, nodes n
			where n.name = '%s' and n.id = b.node""" % host)

		if nrows < 1:
			#
			# insert a new row
			#
			self.db.execute("""insert into boot (node, action)
				values((select id from nodes where name = '%s'),
				"%s") """ % (host, action))
		else:
			#
			# update an existing row
			#
			bootid, = self.db.fetchone()

			self.db.execute("""update boot set action = "%s"
				where id = %s """ % (action, bootid))
		return

	def run(self, params, args):
		(action,) = self.fillParams([('action', )])
		
		if not len(args):
                	raise ArgRequired(self, 'host')

		if action not in [ 'os', 'run', 'install', None ]:
                	raise ParamValue(self, 'action', '"os", "run" or "install"')

		for host in self.getHostnames(args):
			if action:
				self.updateBoot(host, action)

                        #
                        # if this host is the frontend, then generate the
                        # default configuration file
                        #
                        frontend_host = self.db.getHostAttr('localhost', 'Kickstart_PrivateHostname')
                        if host == frontend_host:
                                self.writeDefaultPxebootCfg()
                        else:
				self.writePxebootCfg(host, action)


