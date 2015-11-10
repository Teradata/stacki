#!@PYTHON@

from __future__ import print_function
import os
import sys
import base64
import crypt
import random
import time

class pw:
	def __init__(self):
		s = long(time.time()*pow(10, 9))
		random.seed(s)

	def get_rand(self, num_bytes=16):
		c = ''
		for i in range(num_bytes):
			c = c + chr(random.getrandbits(8))
			random.seed(long(time.time()*pow(10, 9)))
		return c
			
	def get_salt(self):
		salt = '$1$'
		s = self.get_rand()
		salt = salt + base64.urlsafe_b64encode(s)[0:8]
		return salt

	def get_cleartext_pw(self):
		c = self.get_rand()
		c_pw = base64.urlsafe_b64encode(c)
		c_pw = c_pw.rstrip('=')
		return c_pw
		
	def get_crypt_pw(self):
		c_pw = self.get_cleartext_pw()
		salt = self.get_salt()
		return crypt.crypt(c_pw, salt)

if __name__ == '__main__':
	p = pw()
	if len(sys.argv) > 1:
		type = sys.argv[1].strip()
	if type == 'crypt':
		print(p.get_crypt_pw())
	else:
		print(p.get_cleartext_pw())
