#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from __future__ import print_function
import os
import sys
import stack.api
import profile


class Profile(profile.ProfileBase):

	def pre(self, client):

		# Deny all requests that come from non-priviledged ports
		# This means only a root user can request a kickstart file

		if client.port > 1023:
			print("Content-type: text/html")
			print("Status: 401 Unauthorized\n")
			print("<h1>Unauthorized</h1>")
			sys.exit(1)


	def main(self, client):

		report = []
		cmd = '/opt/stack/bin/stack list host xml %s' % client.addr
		for line in os.popen(cmd).readlines():
			report.append(line[:-1])

		#
		# get the avalanche attributes
		#

		result = stack.api.Call('list host attr', [ client.addr ])
		attrs  = {}
		for dict in result:
			if dict['attr'] in [
					'Kickstart_PrivateKickstartHost',
					'trackers',
					'pkgservers' ]:
				attrs[dict['attr']] = dict['value'] 

		if 'trackers' not in attrs:
			attrs['trackers'] = attrs['Kickstart_PrivateKickstartHost']
		if 'pkgservers' not in attrs:
			attrs['pkgservers'] = attrs['Kickstart_PrivateKickstartHost']

		#
		# Done
		#

		if report:
			out = '\n'.join(report)
			print('Content-type: application/octet-stream')
			print('Content-length: %d' % (len(out)))
			print('X-Avalanche-Trackers: %s' % (attrs['trackers']))
			print('X-Avalanche-Pkg-Servers: %s' % (attrs['pkgservers']))
			print('')
			print(out)
		
