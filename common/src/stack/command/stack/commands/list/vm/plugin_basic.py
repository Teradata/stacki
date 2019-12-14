# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'basic'

	def run(self, args):
		hosts, expanded = args
		keys = ['hypervisor', 'memory', 'cpu', 'pending deletion']
		vm_info = self.owner.vm_info(hosts)
		return { 'keys' : keys, 'values': vm_info }
