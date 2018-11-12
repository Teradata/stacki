#! /opt/stack/bin/python
#
# @SI_Copyright@
# @SI_Copyright@

from __future__ import print_function
import os
import sys
import string
import syslog
import stack.api
import profile
import cgi

class Profile(profile.ProfileBase):

        def main(self, client):
		self.form = cgi.FieldStorage()
		try:
			profiletype = self.form['profile'].value
		except:
			profiletype = None

                report = []
		if profiletype == 'full':
			cmd = '/opt/stack/bin/stack list host xml '
			cmd += '%s' % client.addr
		else:
			cmd = '/opt/stack/bin/stack list host profile ' 
			cmd += '%s chapter=preseed document=false' % client.addr

                for line in os.popen(cmd).readlines():
                        report.append(line[:-1])

                #
                # Done
                #
                if report:
                        out = string.join(report, '\n')
                        print('Content-type: application/octet-stream')
                        print('Content-length: %d' % (len(out)))
                        print('')
                        print(out)
		
