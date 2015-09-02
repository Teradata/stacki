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

class Plugin(stack.commands.ApplianceArgumentProcessor, 
	     stack.commands.HostArgumentProcessor,
	     stack.commands.Plugin):

	def provides(self):
		return 'default'

	def run(self, attrs):
		appliances = self.getApplianceNames()
		hosts      = self.getHostnames()

		# Clear out all the attributes represented in the spreadsheet.
		# This prepare us for the next step of adding only the cells 
		# with set values.

		for target in attrs.keys():
			if target == 'default':
				continue
			elif target == 'global':
				if not attrs[target].has_key('environment'):
					cmd = 'remove.attr'
					arg = None
				else:
					cmd = 'remove.environment.attr'
					arg = attrs[target]['environment']
			elif target in appliances:
				cmd = 'remove.appliance.attr'
				arg = target
			else:
				cmd = 'remove.host.attr'
				arg = target

			for attr in attrs[target].keys():
				if arg:
					args = [ arg ]
				else:
					args = []
				args.append('attr=%s' % attr)
				self.owner.call(cmd, args)

		#
		# now add the attributes
		#
		for target in attrs.keys():
			if target == 'default':
				continue
			elif target == 'global':
				if not attrs[target].has_key('environment'):
					cmd = 'set.attr'
					arg = None
				else:
					cmd = 'set.environment.attr'
					arg = attrs[target]['environment']
			elif target in appliances:
				cmd = 'set.appliance.attr'
				arg = target
			else:
				cmd = 'set.host.attr'
				arg = target

			for attr in attrs[target].keys():
				#
				# only add attributes that have a value
				#
				if not attrs[target][attr]:
					continue
				if arg:
					args = [ arg ]
				else:
					args = []
				args.append('attr=%s' % attr)
				args.append('value=%s' % attrs[target][attr])

				self.owner.call(cmd, args)

			# If the environment is set move all the hosts
			# to an environment specific distribuion.

			dist = attrs[target].get('environment')
			if dist:
				if target in hosts:
					self.owner.call('set.host.distribution',
                                                        [ target, 
                                                          'distribution=%s' % dist ])
