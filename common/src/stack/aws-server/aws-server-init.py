#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import sys
import time
import urllib.error
from urllib.request import urlopen 
from stack.api import Call

def lookup(path):
	done = False
	while not done:
		try:
			response = urlopen('http://169.254.169.254/latest/%s' % path)
			done	 = True
		except urllib.error.HTTPError:
			time.sleep(1)
	value = response.read().decode()
	return value

found = False
key   = lookup('meta-data/public-keys/0/openssh-key').strip()
with open('/root/.ssh/authorized_keys', 'r') as f:
	for line in f.readlines():
		if key == line.strip():
			found = True
if not found:
	with open('/root/.ssh/authorized_keys', 'a') as f:
		f.write('%s\n' % key)

