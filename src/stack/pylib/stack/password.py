#! /opt/stack/bin/python
# @SI_Copyright@
# @SI_Copyright@

import string
import crypt
import random

class Enc:
        def enc_crypt(self, value):
        	salt = '$1$'
        	for i in range(0, 8):
        		salt += random.choice(
        		string.ascii_letters +
        		string.digits + './')
        	return crypt.crypt(value, salt)
