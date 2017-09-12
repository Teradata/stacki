#! /opt/stack/bin/python3
#
# @SI_Copyright@
# @SI_Copyright@

import os
import sys
import string
import syslog
import stack.api
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
		
