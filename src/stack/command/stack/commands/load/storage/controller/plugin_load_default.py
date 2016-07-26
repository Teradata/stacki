# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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

class Plugin(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor, stack.commands.Plugin):

	def provides(self):
		return 'default'


	def run(self, args):
		hosts = args

		for host in hosts.keys():
			#
			# first remove all existing entries
			#
			cmdargs = []

			if host != 'global':
				cmdargs.append(host)
			cmdargs += [ 'adapter=*', 'enclosure=*', 'slot=*' ]

			self.owner.call('remove.storage.controller', cmdargs)

			arrayids = hosts[host].keys()
			arrayids.sort()

			for array in arrayids:
				cmdargs = []
				if host != 'global':
					cmdargs.append(host)
				cmdargs += [ 'arrayid=%s' % array ]

				if 'raid' in hosts[host][array].keys():
					raidlevel = hosts[host][array]['raid']
					cmdargs.append('raidlevel=%s'
						% raidlevel)

				if 'slot' in hosts[host][array].keys():
					slots = []
					for slot in hosts[host][array]['slot']:
						if type(slot) == type(0):
							slots.append(
								'%d' % slot)
						else:
							slots.append(slot)

					cmdargs.append('slot=%s'
						% ','.join(slots))

				if 'enclosure' in hosts[host][array].keys():
					enclosure = hosts[host][array]['enclosure'].strip()
					cmdargs.append('enclosure=%s' % enclosure)

				if 'options' in hosts[host][array].keys():
					options = hosts[host][array]['options']
					cmdargs.append('options="%s"' % options)

				if 'hotspare' in hosts[host][array].keys():
					hotspares = []
					for hotspare in hosts[host][array]['hotspare']:
						hotspares.append('%d'
							% hotspare)

					cmdargs.append('hotspare=%s'
						% ','.join(hotspares))

				if self.owner.force:
					cmdargs.append('force=y')
			
				self.owner.call('add.storage.controller',
					cmdargs)

