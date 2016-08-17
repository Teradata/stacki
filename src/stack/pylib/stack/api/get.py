# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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
import ConfigParser
import stack.api

def GetHostname(host='localhost'):
	"""
	Takes the name, ip, or mac of any network interface of the
	HOST and returns the canonical name of the host.  The canonical
	name if the value store in the NODES table of the cluster database.

	If the HOST could not be found it returns None.
	"""

	result = stack.api.Call('list host', [ host ])

	if result:
		assert len(result) == 1
		return result[0]['host']
	
	return None


def GetAttr(attribute):
	"""
	Returns the value of the specified ATTRIBUTE for the caller's host.
	If no attribute is define it returns None.
	"""
	return GetHostAttr('localhost', attribute)


def GetHostAttr(host, attribute):
	"""
	Returns the value of the specified ATTRIBUTE for the given
	HOST.  If no attribute is define it returns None.

        If a profile.cfg file is found read the attribute from there
        rather than from the database.
	"""

        value = None

        cfg = ConfigParser.RawConfigParser()
        cfg.read(os.path.join(os.sep, 'opt', 'stack', 'etc', 'profile.cfg'))
        try:
                value = cfg.get('attr', attribute)
        except:
                result = stack.api.Call('list host attr', 
                                        [host, 'attr=%s' % attribute])
                if result:
                        assert len(result) == 1
                        value = result[0]['value']
		
	return value


if __name__ == "__main__":
	print('GetHostname() ->', GetHostname())
	print('GetHostAttr("localhost", "os") ->', GetHostAttr('localhost', 'os'))
