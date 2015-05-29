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

import shlex
import subprocess
import stack.commands

class Command(stack.commands.set.host.command):
	"""
	Set state for a storage device for hosts (e.g., to change the state
	of a disk from 'offline' to 'online').

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, this
	command will apply the state change to all known hosts.
	</arg>

	<param type='string' name='enclosure' optional='0'>
	An integer id for the enclosure that contains the storage device.
	</param>

	<param type='string' name='slot' optional='0'>
	An integer id for the slot that contains the storage device.
	</param>

	<param type='string' name='action' optional='0'>
	The action to perform on the device. Valid actions are: online,
	offline, configure, locate-on and locate-off.
	</param>

	<example cmd='set host storage compute-0-0 enclosure=32 slot=5
	action=online'>
	Set the storage device located at '32:5' to "online" for compute-0-0.
	</example>
	"""

	def setState(self, host, adapter, encid, slot, action):
		megacmd = None

		if action == 'configure':
			flags = self.db.getHostAttr(host, 'storage.lsi.flags')

			megacmd = '/opt/stack/sbin/MegaCli -CfgForeign -Clear '
			megacmd += '-a%s > /dev/null 2>&1 ' % (adapter)

			megacmd += ' ; '

			megacmd += '/opt/stack/sbin/MegaCli -cfgldadd '
			megacmd += '-r0[%s:%s] ' % (encid, slot)
			if flags:
				megacmd += '%s ' % (flags)
			megacmd += '-a%s > /dev/null 2>&1' % (adapter)

			print 'megacmd: ', megacmd

		elif action == 'offline':
			megacmd = '/opt/stack/sbin/MegaCli -pdoffline '
			megacmd += '-physdrv[%s:%s] ' % (encid, slot)
			megacmd += '-a%s > /dev/null 2>&1' % (adapter)

		elif action == 'online':
			megacmd = '/opt/stack/sbin/MegaCli -pdonline '
			megacmd += '-physdrv[%s:%s] ' % (encid, slot)
			megacmd += '-a%s > /dev/null 2>&1' % (adapter)

		elif action == 'locate-on':
			megacmd = '/opt/stack/sbin/MegaCli -pdlocate -start '
			megacmd += '-physdrv[%s:%s] ' % (encid, slot)
			megacmd += '-a%s > /dev/null 2>&1' % (adapter)

		elif action == 'locate-off':
			megacmd = '/opt/stack/sbin/MegaCli -pdlocate -stop'
			megacmd += '-physdrv[%s:%s] ' % (encid, slot)
			megacmd += '-a%s > /dev/null 2>&1' % (adapter)

		#
		# can't call 'rocks run host' here because the host
		# argument processor tries to interpret ':' as a
		# range of hosts (because it uses fillPositionalArgs!)
		#
		if megacmd:
			cmd = '/usr/bin/ssh -x -q %s "%s"' % (host, megacmd)
			subprocess.call(shlex.split(cmd))


	def run(self, params, args):
		(encid, slot, action) = self.fillParams([ ('enclosure', None),
			('slot', None), ('action', None) ])

		if not encid:
			self.abort('must supply an "enclosure" parameter')
		if not slot:
			self.abort('must supply a "slot" parameter')
		if not action:
			self.abort('must supply an "action" parameter')
		validactions = [ 'online', 'offline', 'configure', 'locate-on',
			'locate-off' ]
		if action not in validactions:
			self.abort('"action" must one of: %s'
				% ', '.join(validactions))

		try:
			encid = int(encid)
		except:
			self.abort('"enclosure" must be an integer')
		try:
			slot = int(slot)
		except:
			self.abort('"slot" must be an integer')

		adapter = 0

		for host in self.getHostnames(args):
			found = 0
			for row in self.call('list.host.storage', [ host ]):
				if row['enclosure'] == encid and \
						row['slot'] == slot:

					found = 1

					if action == 'online' and \
						row['status'] == 'online':

						msg = 'storage device at '
						msg += '%d:%d ' % (encid, slot)
						msg += 'is already online'
						print msg
					elif action == 'offline' and \
						row['status'] == 'offline':

						msg = 'storage device at '
						msg += '%d:%d ' % (encid, slot)
						msg += 'is already offline'
						print msg
					elif action == 'configure' and \
						row['status'] != 'unconfigured':

						msg = 'storage device at '
						msg += '%d:%d ' % (encid, slot)
						msg += 'must be "unconfigured"'
						print msg
					else:
						self.setState(host, adapter,
							encid, slot, action)

					break

			if not found:
				msg = 'storage device %d:%d ' % (encid, slot)
				msg += 'was not found on host %s' % host
				print msg

