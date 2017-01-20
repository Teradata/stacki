#
# @SI_Copyright@
#                               stacki.com
#                                  v3.3
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

import os
import stack.commands
import stack.ip

class Implementation(stack.commands.Implementation):	
	"""
	Output /etc/chrony.conf
	"""

	def client(self, host, timeserver):
		self.owner.addOutput(host, '<stack:file stack:name="/etc/chrony.conf">')
		self.owner.addOutput(host, 'server %s' % timeserver)
		self.owner.addOutput(host, 'allow %s' % timeserver)
		self.owner.addOutput(host, 'local stratum 10')
		self.owner.addOutput(host, 'driftfile /var/lib/chrony/drift')
		self.owner.addOutput(host, 'logdir /var/log/chrony')
		self.owner.addOutput(host, 'log measurements statistics tracking')
		self.owner.addOutput(host, '</stack:file>')


	def server(self, host, timeserver):
		network = None
		output = self.owner.call('list.host.interface', [ host ])
		for o in output:
			if o['default']:
				network = o['network']
				break
		if not network:
			return

		address = None
		mask = None
		output = self.owner.call('list.network', [ network ])
		for o in output:
			address = o['address']
			mask = o['mask']
		if not address or not mask:
			return

		ip = stack.ip.IPGenerator(address, mask)

		self.owner.addOutput(host, '<stack:file stack:name="/etc/chrony.conf">')
		self.owner.addOutput(host, 'server %s iburst' % timeserver)
		self.owner.addOutput(host, 'local stratum 10')
		self.owner.addOutput(host, 'stratumweight 0')
		self.owner.addOutput(host, 'driftfile /var/lib/chrony/drift')
		self.owner.addOutput(host, 'rtcsync')
		self.owner.addOutput(host, 'allow %s/%s' % (address, ip.cidr()))
		self.owner.addOutput(host, 'bindcmdaddress 127.0.0.1')
		self.owner.addOutput(host, 'bindcmdaddress ::1')
		self.owner.addOutput(host, 'logchange 0.5')
		self.owner.addOutput(host, 'logdir /var/log/chrony')
		self.owner.addOutput(host, 'log measurements statistics tracking')
		self.owner.addOutput(host, '</stack:file>')


	def run(self, args):
		(host, appliance, timeserver) = args

		self.owner.addOutput(host, "kill `pidof chronyd`")

		self.owner.addOutput(host, '/sbin/chkconfig chronyd on')
		self.owner.addOutput(host, '/sbin/chkconfig ntp off')

		if appliance == 'frontend':
			self.server(host, timeserver)
		else:
			self.client(host, timeserver)

		#
		# set the time right now
		#
		self.owner.addOutput(host, 'pidof chronyd')
		self.owner.addOutput(host, 'while [ $? -eq 0 ]')
		self.owner.addOutput(host, 'do')
		self.owner.addOutput(host, '\tsleep 1')
		self.owner.addOutput(host, '\tkill -9 `pidof chronyd`')
		self.owner.addOutput(host, '\tpidof chronyd')
		self.owner.addOutput(host, 'done')

		self.owner.addOutput(host,
			"/usr/sbin/chronyd -q 'server %s iburst'" % timeserver)

