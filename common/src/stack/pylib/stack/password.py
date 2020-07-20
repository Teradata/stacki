#! /opt/stack/bin/python
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import crypt
import os
import random
import time
import string


class Password:
	def get_rand(self, num_bytes=16, choices=string.ascii_letters + string.digits):
		password = ''
		for _ in range(num_bytes):
			# Note: The `getrandom` system call will never block once the entropy
			# pool has been initialized, which seems to happen before any of our
			# code would ever run, probably due to only needing to collect 4096 bits
			# of entropy. The RDRAND x86 instruction has been available since 2012
			# and the Linux kernel will use it to initialize the entropy pool.

			try:
				# Try seeding random in a non-blocking way
				# Note: Using 64 bits (8 bytes) of entropy per password byte
				random.seed(os.getrandom(8, flags=os.GRND_NONBLOCK))
			except BlockingIOError:
				# Blocked getting entropy from the OS, so use milliseconds instead
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
