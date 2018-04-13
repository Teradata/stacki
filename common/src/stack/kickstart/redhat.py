#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import sys
import stack.api
import subprocess
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
			attrs['trackers']   = attrs['Kickstart_PrivateKickstartHost']
		if 'pkgservers' not in attrs:
			attrs['pkgservers'] = attrs['Kickstart_PrivateKickstartHost']


		p = subprocess.run(['/opt/stack/bin/stack', 'list', 'host', 'xml', client.addr ],
				   stdout=subprocess.PIPE,
				   stderr=subprocess.PIPE)
		rc  = p.returncode
		doc = [ ]

		if rc == 0:
			doc.append('Content-type: application/octet-stream')
			doc.append('Content-length: %d' % len(p.stdout))
			doc.append('X-Avalanche-Trackers: %s' % (attrs['trackers']))
			doc.append('X-Avalanche-Pkg-Servers: %s' % (attrs['pkgservers']))
			doc.append('')
			doc.append(p.stdout.decode())
		else:
			doc.append('Content-type: text/html')
			doc.append('Status: 500 Server Error')
			doc.append('Retry-After: 60')
			doc.append('')
			doc.append(p.stderr.decode())
		
		print('\n'.join(doc))
		
