# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.list.command):
	"""
	Lists the available PXE OS Install targets.
	
	<example cmd='list bootaction'>
	Lists the available PXE OS Install targets.
	</example>
	"""

	def run(self, params, args):

		(req_type, req_os) = self.fillParams([
			('type', None),
			('os', None)])

		self.beginOutput()

		for (b_action, b_type, b_os, b_kernel, b_ramdisk, b_args) in self.db.select(
				"""
				bn.name, bn.type, o.name, ba.kernel, ba.ramdisk, ba.args from 
				bootactions ba 
				inner join bootnames bn on ba.bootname = bn.id 
				left join oses o on ba.os = o.id
				"""):

			if req_type is not None and req_type != b_type:
				continue

			if req_os is not None and (b_os is not None and req_os != b_os):
				continue

			if args and b_action not in args:
				continue
			
			self.addOutput(b_action, (b_type, b_os, b_kernel, b_ramdisk, b_args))

		self.endOutput(header=[ 'bootaction', 'type', 'os', 'kernel', 'ramdisk', 'args'])

