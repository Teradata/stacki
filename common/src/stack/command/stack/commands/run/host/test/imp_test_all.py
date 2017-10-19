# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import rocks.commands
import salt.client

class Implementation(rocks.commands.Implementation):
	def run(self, args):
		hosts, prefix = args

		if not prefix:
			prefix = "/tmp/test"

		for test in [ 'memory', 'disk', 'network' ]:
			print 'running "%s" test' % test
			output = self.owner.command('run.host.test', hosts +
				[ 'test=%s' % test, 'output-format=json' ])

			file = open('%s.%s' % (prefix, test), 'w+')
			file.write(output)
			file.close()

