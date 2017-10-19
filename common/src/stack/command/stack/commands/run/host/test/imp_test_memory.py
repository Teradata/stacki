# @copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @copyright@


import rocks.commands
import salt.client

class Implementation(rocks.commands.Implementation):
	def run(self, args):
		hosts, extras = args

		self.owner.fields = [ "host", "test", "MB/s" ]

		s = salt.client.LocalClient()
		out = s.cmd(hosts, "stream.run", expr_form="list")
		for o in out:
			for result in out[o]:
				if type(result) == type({}) and \
						result.has_key('test') and \
						result.has_key('best'):
					self.owner.addOutput(o,
						(result['test'],
						result['best']))

