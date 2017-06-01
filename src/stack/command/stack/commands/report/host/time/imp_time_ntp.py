#
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

import os
import stack.commands

class Implementation(stack.commands.Implementation):	
	"""
	Output /etc/ntp.conf
	"""

	def client(self, host, timeserver):
		#
		# configure NTP to use an external server
		#
		self.owner.addOutput(host, '<stack:file stack:name="/etc/ntp.conf">')
		self.owner.addOutput(host, 'server %s' % timeserver)
		self.owner.addOutput(host, 'driftfile /var/lib/ntp/drift')
		self.owner.addOutput(host, '</stack:file>')

		#
		# force the clock to be set on next boot
		#
		self.owner.addOutput(host, 'mkdir -p /etc/ntp')
		self.owner.addOutput(host, '<stack:file stack:name="/etc/ntp/step-tickers">')
		self.owner.addOutput(host, '%s' % timeserver)
		self.owner.addOutput(host, '</stack:file>')


	def server(self, host, timeserver):
		self.owner.addOutput(host, '<stack:file stack:name="/etc/ntp.conf">')
		self.owner.addOutput(host, 'server %s iburst' % timeserver)
		self.owner.addOutput(host, 'server 127.127.1.1 iburst')
		self.owner.addOutput(host, 'fudge 127.127.1.1 stratum 10')
		self.owner.addOutput(host, 'driftfile /var/lib/ntp/drift')
		self.owner.addOutput(host, '</stack:file>')


	def run(self, args):
		(host, appliance, timeserver) = args

		self.owner.addOutput(host, '/sbin/chkconfig ntpd on')
		self.owner.addOutput(host, '/sbin/chkconfig chronyd off')

		self.owner.addOutput(host,
			'<stack:file stack:name="/etc/cron.hourly/ntp" stack:perms="0755">')
		self.owner.addOutput(host, '#!/bin/sh')
		self.owner.addOutput(host, 'if ! ( /usr/sbin/ntpq -pn 2&gt; /dev/null | grep -e \'^\*\' &gt; /dev/null ); then')
		self.owner.addOutput(host, '    /etc/rc.d/init.d/ntpd restart &gt; /dev/null 2&gt;&amp;1')
		self.owner.addOutput(host, 'fi')
		self.owner.addOutput(host, '</stack:file>')

		self.owner.addOutput(host, '<stack:file stack:name="/etc/sysconfig/ntpd">')
		self.owner.addOutput(host,
			'OPTIONS="-A -u ntp:ntp -p /var/run/ntpd.pid"')
		self.owner.addOutput(host, '</stack:file>')

		if appliance == 'frontend':
			self.server(host, timeserver)
		else:
			self.client(host, timeserver)

		#
		# set the clock right now
		#
		self.owner.addOutput(host, '/usr/sbin/ntpdate %s' % timeserver)

