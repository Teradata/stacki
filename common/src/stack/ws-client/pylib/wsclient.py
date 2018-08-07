# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


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
			raise IOError(f'File {filename} does not exist')
		
		if 'Content-Type' in self.session.headers:
			del self.session.headers['Content-Type']
		
		response = self.session.post(f'{self.url}/upload', files={
			'csvFile': (os.path.basename(filename), open(filename, 'rb'), 'text/csv')
		})

		output = response.json()
		if output:
			return output['dir']
