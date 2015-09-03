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

import shlex
import subprocess
import stack.commands
from stack.exception import *

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
                # TODO: Revist now that fillPositionArgs is dead
		#
		if megacmd:
			cmd = '/usr/bin/ssh -x -q %s "%s"' % (host, megacmd)
			subprocess.call(shlex.split(cmd))


	def run(self, params, args):
		(encid, slot, action) = self.fillParams([
                        ('enclosure', None, True),
			('slot', None, True),
                        ('action', None, True) ])

		validactions = [ 'online', 'offline', 'configure', 'locate-on',
			'locate-off' ]
		if action not in validactions:
                        raise CommandError(self, '"action" must one of: %s' % ', '.join(validactions))

		try:
			encid = int(encid)
		except:
                        raise CommandError(self, '"enclosure" must be an integer')
		try:
			slot = int(slot)
		except:
			raise CommandError(self, '"slot" must be an integer')

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

