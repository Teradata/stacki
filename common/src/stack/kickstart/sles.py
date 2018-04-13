#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import subprocess
import profile


class Profile(profile.ProfileBase):

	def main(self, client):

		p = subprocess.run(['/opt/stack/bin/stack', 'list', 'host', 'xml', client.addr ],
				   stdout=subprocess.PIPE,
				   stderr=subprocess.PIPE)
		rc  = p.returncode
		doc = [ ]

		if rc == 0:
			doc.append('Content-type: application/octet-stream')
			doc.append('Content-length: %d' % len(p.stdout))
			doc.append('')
			doc.append(p.stdout.decode())
		else:
			doc.append('Content-type: text/html')
			doc.append('Status: 500 Server Error')
			doc.append('Retry-After: 60')
			doc.append('')
			doc.append(p.stderr.decode())
		
		print('\n'.join(doc))
		
