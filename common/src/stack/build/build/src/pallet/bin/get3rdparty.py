#!/usr/bin/python
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import sys
import subprocess
import time

urlbase   = 'https://teradata-stacki.s3.amazonaws.com/3rdparty'
manifest  = 'manifest.3rdparty'
cachedir  = '3rdparty'
docfile   = '3rdparty.md'
resources = { }

if not os.path.exists(manifest):
	print('no manifest.3rdparty found')
	sys.exit(0)

if not os.path.exists(cachedir):
	os.mkdir(cachedir)

fin = open(manifest, 'r')
for line in fin.readlines():
	resource = line.strip()
	resources[resource] = os.path.join(urlbase, resource)
fin.close()

for resource in resources:
	target = os.path.join(cachedir, resource)
	if not os.path.exists(target):
		retry = 3
		while retry:
			print('download %s\n\t%s' % (resource, resources[resource]))
			cmd_line = [ 'curl',
					'--retry','2',
					'-w','%{http_code}',
					'-sSo%s' % target,
					resources[resource] ]
			p = subprocess.Popen(cmd_line,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE)
			rc = p.wait()
			o, e = p.communicate()
			if rc:
				retry = retry - 1
				print(e)
				time.sleep(1)
			else:
				if o.strip() == '200':
					retry = 0
				else:
					retry = retry - 1
					print("Error: Cannot download. HTTP STATUS: %s" % o)
					os.unlink(target)
					time.sleep(1)

fout = open(docfile, 'w')
fout.write("""# Third Party Resources

This repository includes the following code from other projects.

""")
for resource in sorted(resources.keys()):
	fout.write('* %s [%s]\n' % (resource, resources[resource]))

fout.close()









