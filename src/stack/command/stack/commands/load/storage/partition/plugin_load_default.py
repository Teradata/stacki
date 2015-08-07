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

import stack.commands

class Plugin(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor, stack.commands.Plugin):

	"""
	Plugin that invokes 'stack add storage partition' and adds
	the partitions to the database.
	"""
	def provides(self):
		return 'default'


	def run(self, args):
		hosts = args
		for host in hosts.keys():
			# Get list of devices for this host
			devices = hosts[host].keys()
			devices.sort()

			# Loop through all devices in the list
			for device in devices:
				partition_list = hosts[host][device]

				# Add storage partitions for this device
				for partition in partition_list:
					cmdargs = []
					if host != 'global':
						cmdargs.append(host)
					cmdargs += [ 'device=%s' % device ]

					mountpt = partition['mountpoint']
					size = partition['size']
					type = partition['type']
					options = partition['options']

					cmdargs.append('mountpoint=%s' % mountpt)
					cmdargs.append('size=%s' % size)
					cmdargs.append('type=%s' % type)
					if options:
						cmdargs.append('options="%s"' % options)

					self.owner.call('add.storage.partition',
						cmdargs)
