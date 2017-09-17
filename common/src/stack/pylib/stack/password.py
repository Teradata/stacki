#! /opt/stack/bin/python
# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import base64
import crypt
import os


class Password:
	def get_cleartext_pw(self, c_pw=None):
		if not c_pw:
			c = os.urandom(16)
			c_pw = base64.urlsafe_b64encode(c).rstrip(b'=')
		
		return c_pw.decode()

	def get_crypt_pw(self, c_pw=None):
		# if c_pw was not specified, generate a random password
		if not c_pw:
			c_pw = self.get_cleartext_pw()
		
		return crypt.crypt(c_pw)
