# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
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

