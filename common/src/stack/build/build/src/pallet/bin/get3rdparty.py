#!/usr/bin/python
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import sys
import json
import subprocess

filename  = '3rdparty.json'
cachedir  = '3rdparty'
docfile	  = '3rdparty.md'

if not os.path.exists(filename):
	print('no %s found' % filename)
	sys.exit(0)

if not os.path.exists(cachedir):
	os.mkdir(cachedir)

with open(filename, 'r') as text:
	code = []
	for line in text: # json doesn't allow comments (we do)
		if not line.startswith('//'):
			code.append(line)
	manifest = json.loads(''.join(code))

blobs = {}
for section in manifest:
	for blob in section['files']:
		blobs[blob] = { 
			'source' : os.path.join(section['urlbase'], blob),
			'target' : os.path.join(cachedir, blob)
		}


for blob in blobs:
	if not os.path.exists(blobs[blob]['target']):
		print('download %s\n\t%s' % (blob, blobs[blob]['source']))
		subprocess.call([ 'curl', '-sSo%s' % blobs[blob]['target'], blobs[blob]['source'] ])


with open(docfile, 'w') as fout:
	fout.write('# Third Party Blobs\n\n')
        fout.write('This repository includes the following code from other projects.\n\n')
	for blob in sorted(blobs.keys()):
		fout.write('* %s [%s]\n' % (blob, blobs[blob]['source']))

fout.close()









