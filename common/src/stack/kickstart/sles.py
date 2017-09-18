#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import profile


class Profile(profile.ProfileBase):

	def main(self, client):

		report = []
		cmd = '/opt/stack/bin/stack list host xml %s' % client.addr
		for line in os.popen(cmd).readlines():
			report.append(line[:-1])

		if report:
			out = '\n'.join(report)
			print('Content-type: application/octet-stream')
			print('Content-length: %d' % len(out))
			print('')
			print(out)
		
