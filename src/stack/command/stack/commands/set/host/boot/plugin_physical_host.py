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

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'physical-host'

	def writeDefaultPxebootCfg(self):
		nrows = self.db.execute("""select kernel, ramdisk, args from
			bootaction where action='install' """)

		if nrows == 1:
			kernel, ramdisk, args = self.db.fetchone()

			filename = '/tftpboot/pxelinux/pxelinux.cfg/default'
			file = open(filename, 'w')
			file.write('default rocks\n')
			file.write('prompt 0\n')
			file.write('label rocks\n')

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


	def writePxebootCfg(self, host):

		# Get the IP and NETMASK of the host, allow the
		# network.private.netmask attribute to override the
		# networks table.

		netmask = self.db.getHostAttr(host, 'network.private.netmask')
		for row in self.owner.call('list.host.interface', [ host ]):
			if row['subnet'] == 'private':
				ip = row['ip']
				if not netmask:
					netmask = row['netmask']


		# Compute the HEX IP filename for the host
		filename = '/tftpboot/pxelinux/pxelinux.cfg/'
		for i in string.split(ip, '.'):
			hexstr = '%02x' % (int(i))
			filename += '%s' % hexstr.upper()


		#
		# there is a case where the host name may be in the nodes table
		# but not in the boot table. in this case, remove the current
		# configuration file (if it exists) and return
		#

		action = None
		for row in self.owner.call('list.host.boot', [ host ]):
			action = row['action']
		if not action:
			try:
				os.unlink(filename)
			except:
				pass
			return

		# Get the bootaction for the host (install or os) and
		# lookup the actual kernel, ramdisk, and args for the
		# specific action.

		for row in self.owner.call('list.host', [ host ]):
			if action == 'install':
				bootaction = row['installaction']
			else:
				bootaction = row['runaction']

		kernel = ramdisk = args = None
		for row in self.owner.call('list.bootaction'):
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

			for row in self.owner.call('list.host.route', [ host ]):
				if row['network'] == '0.0.0.0' and row['netmask'] == '0.0.0.0':
					gateway = row['gateway']

			dnsserver  = self.db.getHostAttr(host, 'Kickstart_PrivateDNSServers')
			nextserver = self.db.getHostAttr(host, 'Kickstart_PrivateKickstartHost')
			
			override   = self.db.getHostAttr(host, 'network.private.gateway')
			if override:
				gateway = override

			args += ' ip=%s gateway=%s netmask=%s dns=%s nextserver=%s' % \
				(ip, gateway, netmask, dnsserver, nextserver)

		if filename != None:
			file = open(filename, 'w')	
			file.write('default rocks\n')
			file.write('prompt 0\n')
			file.write('label rocks\n')

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
			os.system('chown root.apache %s' % (filename))
			os.system('chmod 664 %s' % (filename))


	def run(self, host):
		#
		# if this host is the frontend, then generate the
		# default configuration file
		#
		frontend_host = self.db.getHostAttr('localhost', 'Kickstart_PrivateHostname')
		if host == frontend_host:
			self.writeDefaultPxebootCfg()
		else:
			#
			# only write PXE configuration file for 'real'
			# machines (e.g., not VMs)
			#
			physnode = True

			nrows = self.db.execute("show tables like 'vm_nodes'")
			if nrows == 1:
                                # HVM Virtual Machines act like Physical
				# Hosts. Treat them that way
				nrows = self.db.execute("""select vn.id from
					vm_nodes vn, nodes n
					where vn.node = n.id and
					vn.virt_type != 'hvm' and
					n.name = "%s" """ % (host))
				if nrows == 1:
					physnode = False

			if physnode:
				self.writePxebootCfg(host)

