#!/opt/stack/bin/python3
# 
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import sys
import os
import subprocess

root = sys.argv[1]
rpms = sys.argv[2:]

for name in rpms:
	p = subprocess.run(['yumdownloader', '-d0', '--urls', name],
			   stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	for line in p.stdout.decode().split('\n'):
		subprocess.call(['rpm', '-i', '--force', '--excludedocs',
				 '--badreloc', '--relocate', '/=%s' % root,
				 '--nodeps', line])

