#
# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@
#

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

