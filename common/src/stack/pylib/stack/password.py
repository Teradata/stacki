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
import string


class Password:
	def get_rand(self, num_bytes=16):
		choices = string.ascii_letters + string.digits

		password = ''
		for _ in range(num_bytes):
			random.seed(int(time.time() * pow(10, 9)))
			password += random.choice(choices)

		return password.encode()

	def get_salt(self):
		salt = '$1$'
		s = self.get_rand()
		salt = salt + base64.urlsafe_b64encode(s)[0:8].decode()
		return salt

	def get_cleartext_pw(self, c_pw=None):
		if not c_pw:
			c_pw = self.get_rand().decode()
		return c_pw

	def get_crypt_pw(self, c_pw=None):
		# if c_pw was not specified, generate a random password
		if not c_pw:
			c_pw = self.get_cleartext_pw()
		salt = self.get_salt()

		return crypt.crypt(c_pw, salt)
