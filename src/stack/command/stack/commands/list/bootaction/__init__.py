# @SI_Copyright@
# @SI_Copyright@

import sys
import socket
import string
from stack.exception import *
import stack.commands

class Command(stack.commands.list.command):
	"""
	Lists the available PXE OS Install targets.
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

			if req_type == '':
				if b_type != None:
					continue
			elif req_type and req_type != b_type:
				continue

			if req_os == '':
				if b_os != None:
					continue
			elif req_os and req_os != b_os:
				continue

			if args and b_action not in args:
				continue
			
			self.addOutput(b_action, (b_type, b_os, b_kernel, b_ramdisk, b_args))

		self.endOutput(header=[ 'bootaction', 'type', 'os', 'kernel', 'ramdisk', 'args'])

