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


def download_url(source, target, curl_args):
	# Retry the curl command 3 times, in case of error
	retry = 3
	curl_cmd = [ 'curl','--retry','2','-w','%{http_code}']

	# Append any extra curl arguments specified
	if len(curl_args):
		curl_cmd.extend(curl_args)
	curl_cmd.extend(['-sSo%s' % target, source])
	print('download %s\n\t%s' % (source, target))
	print (' '.join(curl_cmd))
	while retry:
		p = subprocess.Popen(curl_cmd,
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

def get_auth_info(authfile, url):
	curl_args = []
	if not os.path.exists(authfile):
		sys.stderr.write("Cannot find auth file %s for %s\n" % \
			(authfile, url))
	auth = None
	with open(authfile, 'r') as a:
		auth = json.load(a)

	if not auth:
		sys.stderr.write("Cannot read auth file %s for %s\n" % \
			(authfile, url))

	if auth['type'].lower() == 'basic':
		if not 'username' in auth:
			sys.stderr.write("'username' for %s not found in authfile\n" % url)
		if not 'password' in auth:
			sys.stderr.write("'password' for %s not found in authfile\n" % url)
		curl_args = ['-u', '%s:%s' % (auth['username'], auth['password'])]
	elif auth['type'].lower() == 'artifactory':
		if not 'key' in auth:
			sys.stderr.write("Artifactory API key for %s not found in authfile\n" % url)
		curl_args = ['-H','X-JFrog-Art-Api: %s' % auth['key']]

	return curl_args


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

fout = open(docfile, 'w')
fout.write('# Third Party Blobs\n\n')
fout.write('This repository includes the following code from other projects.\n\n')

blobs = {}
for section in manifest:
	if 'authfile' in section:
		curl_args = get_auth_info(section['authfile'], section['urlbase'])
		if not len(curl_args):
			sys.stderr.write('No Credentials for %s' % section['urlbase'])
			continue
	else:
		curl_args = []

	for blob in section['files']:
		blobs[blob] = {
			'source' : os.path.join(section['urlbase'], blob),
			'target' : os.path.join(cachedir, blob)
		}

	for blob in blobs:
		if not os.path.exists(blobs[blob]['target']):
			dirname = os.path.dirname(blobs[blob]['target'])
			if not os.path.exists(dirname):
				os.makedirs(dirname)
			download_url(blobs[blob]['source'], blobs[blob]['target'], curl_args)

	for blob in sorted(blobs.keys()):
		fout.write('* %s [%s]\n' % (blob, blobs[blob]['source']))

fout.close()
