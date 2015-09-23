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

import stack.commands
from stack.exception import *

class Plugin(stack.commands.NetworkArgumentProcessor, stack.commands.Plugin):

	def provides(self):
		return 'default'

	def removeNetwork(self, networks):
		setlist = []
		for k in networks.keys():
			if k in self.getNetworkNames():
				try:
					self.owner.call('remove.network', 
					[ '%s' % k])
				except:
					setlist.append(k)
		return setlist

	def returnDiffs(self,network):
		for k,v in self.networks[network].iteritems():
			self.networks[network][k] = str(v or '')

		for k,v in self.current_networks[network].iteritems():
			self.current_networks[network][k] = str(v or '')
		a = set(self.current_networks[network].items())
		b = set(self.networks[network].items())
		c = b - a
		return c

	def run(self, args):
		self.networks,self.current_networks = args
		netsforset = self.removeNetwork(self.networks)
		for network in self.networks:
			if network in netsforset:
				# get the diffs between what is and what is to be
				diffs = self.returnDiffs(network)
				for diff in diffs:
					setnetargs = [network, str('%s=%s' \
							% (diff[0], diff[1]))]
					self.owner.call('set.network.%s' % 
							diff[0], setnetargs)

			else:
				addnetargs = [network]
				for k,v in self.networks[network].items():
					addnetargs.append("%s=%s" % (k,v))
				self.owner.call('add.network', addnetargs)
