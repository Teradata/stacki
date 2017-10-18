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
import requests

import json
from stack.bool import str2bool

import http.client
import logging

if 'STACKDEBUG' in os.environ:
	http.client.HTTPConnection.debuglevel = 1

	logging.basicConfig(level=logging.DEBUG)
	requests_log = logging.getLogger("requests.packages.urllib3")
	requests_log.setLevel(logging.DEBUG)
	requests_log.propagate = True

class StackWSClient:
	def __init__(self, hostname, username, key):
		self.hostname = hostname
		self.username = username
		self.key      = key
		self.url      = "http://%s/stack" % self.hostname
		self.session  = None
		self.logged_in= False

	def login(self):
		if not self.logged_in:
			self.session = requests.Session()
			resp = self.session.get(self.url)

			csrftoken = resp.cookies['csrftoken']
			self.session.headers.update({
				"csrftoken":csrftoken, 
				"X-CSRFToken":csrftoken,
				})
			resp = self.session.post("%s/login" % self.url,
				data = {"USERNAME":self.username,"PASSWORD":self.key})
			if resp.status_code != 200:
				resp.raise_for_status()
				self.logged_in = False
			self.csrftoken = resp.cookies['csrftoken']
			self.sessionid = resp.cookies['sessionid']

			self.session.headers.update({
				"csrftoken": self.csrftoken,
				"X-CSRFToken":self.csrftoken,
				"sessionid":self.sessionid,
				})
			self.logged_in = True
		
	def run(self, cmd):
		if not self.logged_in:
			self.login()
		if cmd.startswith('load ') or \
			cmd.startswith('unload '):
			new_cmd = self.loadFile(cmd)
			cmd = new_cmd

		self.session.headers.update({"Content-Type": "application/json"})
		js = json.dumps({"cmd":cmd})
		resp = self.session.post(self.url, data = js)
		try:
			out = json.loads(resp.json())
			return json.dumps(out)
		except:
			out = resp.text
			return out

	def loadFile(self, cmd):
		c = cmd.split()
		filename = None
		new_cmd = []
		while c:
			arg = c.pop(0)
			if arg.startswith("file="):
				filename = arg.split('=')[1]
			else:
				new_cmd.append(arg)

		if not filename:
			raise RuntimeError("File argument not specified")
		new_filename = self.upload(filename)
		new_cmd.append("file=%s" % new_filename)
		cmd = ' '.join(new_cmd)
		return cmd

	def upload(self, filename):
		if not os.path.exists(filename) or not os.path.isfile(filename):
			raise IOError("File %s does not exist" % filename)
		basename = os.path.basename(filename)
		f = { "csvFile": (basename, open(filename, 'rb'), 'text/csv')}
		upload_url = "%s/upload/" % self.url
		resp = self.session.post(upload_url, files = f)
		out = resp.json()
		if out:
			return out['dir']
