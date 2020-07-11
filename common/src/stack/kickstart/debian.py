#! /opt/stack/bin/python3
#
# @copyright@
# @copyright@


import sys
import stack.api
import subprocess
import profile


class Profile(profile.ProfileBase):

	def main(self, client):

		p = subprocess.run(['/opt/stack/bin/stack', 'list', 'host', 'profile', 'chapter=main', client.addr ],
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
		
