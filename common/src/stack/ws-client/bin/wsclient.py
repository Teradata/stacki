#!/opt/stack/bin/python3

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
#

import os
import sys
import json

import wsclient

#
# EXAMPLE CLIENT APPLICATION TO ACCESS WEBSERVICE
#

def getCredentialsFile(args):
	if '-f' in args:
		idx = args.index('-f')
		cred_file = args.pop(idx+1)
		args.pop(idx)
	else:
		homedir = os.getenv("HOME")
		cred_file = "%s/stacki-ws.cred" % homedir
	if not os.path.exists(cred_file):
		sys.stderr.write('Cannot file credential file %s\n' % cred_file)
		sys.exit(1)
	return cred_file

def parseCredentials(cred_file):
	cred = open(cred_file, 'r')
	j = json.load(cred)
	hostname = j['hostname']
	username = j['username']
	key	 = j['key']
	return (hostname, username, key)

if __name__ == '__main__':
	cred_file = getCredentialsFile(sys.argv)
	hostname, username, key = parseCredentials(cred_file)

	wsClient = wsclient.StackWSClient(hostname, username, key)
	wsClient.login()

	if len(sys.argv) < 2:
		sys.exit(1)

	cmd = ' '.join(sys.argv[1:])
	out = wsClient.run(cmd)
	print(out)
