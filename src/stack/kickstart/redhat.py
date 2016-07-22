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
                cmd = '/opt/stack/bin/stack list host xml arch=%s os=%s %s' % (client.arch, client.os, client.addr)
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

                if not attrs.has_key('trackers'):
                        attrs['trackers'] = attrs['Kickstart_PrivateKickstartHost']
                if not attrs.has_key('pkgservers'):
                        attrs['pkgservers'] = attrs['Kickstart_PrivateKickstartHost']

                #
                # Done
                #

                if report:
                        out = string.join(report, '\n')
                        print('Content-type: application/octet-stream')
                        print('Content-length: %d' % (len(out)))
                        print('X-Avalanche-Trackers: %s' % (attrs['trackers']))
                        print('X-Avalanche-Pkg-Servers: %s' % (attrs['pkgservers']))
                        print('')
                        print(out)
		
