#! /opt/stack/bin/python
#
# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
		
