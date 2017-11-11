#! /opt/stack/bin/python
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import crypt
import random
import time
import string


class Password:
	def get_rand(self, num_bytes=16, choices=string.ascii_letters + string.digits):
		password = ''
		for _ in range(num_bytes):
			random.seed(int(time.time() * pow(10, 9)))
			password += random.choice(choices)

		return password

	def get_salt(self):
		return '$6${}'.format(
			self.get_rand(choices=string.ascii_letters + string.digits + './')
		)

	def get_cleartext_pw(self, c_pw=None):
		if not c_pw:
			c_pw = self.get_rand()
		return c_pw

	def get_crypt_pw(self, c_pw=None):
		# if c_pw was not specified, generate a random password
		if not c_pw:
			c_pw = self.get_cleartext_pw()
		salt = self.get_salt()

		return crypt.crypt(c_pw, salt)
