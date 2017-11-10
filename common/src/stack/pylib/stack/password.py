#! /opt/stack/bin/python
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import base64
import crypt
import random
import time


class Password:
	def __init__(self):
		s = int(time.time() * pow(10, 9))
		random.seed(s)

	def get_rand(self, num_bytes=16):
		c = ''
		for i in range(num_bytes):
			c = c + chr(random.getrandbits(8))
			random.seed(int(time.time() * pow(10, 9)))
		return c.encode()

	def get_salt(self):
		salt = '$1$'
		s = self.get_rand()
		salt = salt + base64.urlsafe_b64encode(s)[0:8].decode()
		return salt

	def get_cleartext_pw(self, c_pw=None):
		if not c_pw:
			c = self.get_rand()
			c_pw = base64.urlsafe_b64encode(c)
			c_pw = c_pw.rstrip(b'=').decode()
		return c_pw

	def get_crypt_pw(self, c_pw=None):
		# if c_pw was not specified, generate a random password
		if not c_pw:
			c_pw = self.get_cleartext_pw()
		salt = self.get_salt()
		return crypt.crypt(c_pw, salt)
