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
import time

# JSON Structure
# 3rdparty.json
# The URLbase is the baseurl for all files
# The authfile is the file that contains authentication
# and authorization information to access <urlbase>/file
#
# urlbase: typically a web address pointing to a directory
# example: https://teradata-stacki.s3.amazonaws.com/3rdparty
#
# files: the files present at the location
# example: foundation-python-3.6.1-sles11.x86_64.rpm
#
# authfile: optional - Only required when accessing URLS that require authentication
# manifest: optional - Create a manifest directory and an entry for each package in files if they are RPM's
#
# [
#	{
#		"urlbase": "<baseurl1>",
#		"files": [ "file1", "file2", ... ],
#		"authfile": "<authfile1>.json",
#		"manifest": true
#	},
#	{
#		"urlbase": "<baseurl2>",
#		"files": [ "file3", "file4", ... ],
#	}
# ]
#
# JSON Structure
# authfile_basic.json
# {
#	"type": "basic",
#	"username":"<username>",
#	"password":"<password>"
# }
#
# authfile_artifactory.json
# {
#	"type": "artifactory",
#	"key:"<apikey>"
# }

def download_url(source, target, curl_args):
	# Retry the curl command 3 times, in case of error
	retry = 3
	curl_cmd = [ 'curl','--retry','2','-w','%{http_code}']

	# Append any extra curl arguments specified
	if len(curl_args):
		curl_cmd.extend(curl_args)
	curl_cmd.extend(['-sSo%s' % target, source])
	print('download %s\n\t%s' % (source, target))
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


def create_manifest(manifestd, filename):
	rpmcmd = ['rpm', '-qp', filename, '--queryformat', "%{NAME}"]
	proc = subprocess.Popen(rpmcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, error = proc.communicate()

	if proc.returncode == 1:
		return
	pkgname = output
	with open(os.path.join(manifestd, pkgname + '.manifest'), 'w') as mfestfi:
		mfestfi.write(pkgname)


manifest_dir = './manifest.d'
if len(sys.argv) > 1:
	manifest_dir = os.path.join(sys.argv[1], 'manifest.d')

filename  = '3rdparty.json'
cachedir  = '3rdparty'
docfile	  = '3rdparty.md'

if not os.path.exists(filename):
	print('no %s found' % filename)
	sys.exit(0)

if not os.path.exists(cachedir):
	os.mkdir(cachedir)

if not os.path.exists(manifest_dir):
	os.mkdir(manifest_dir)

with open(filename, 'r') as text:
	code = []
	for line in text: # json doesn't allow comments (we do)
		if not line.startswith('//'):
			code.append(line)
	pkglist = json.loads(''.join(code))

fout = open(docfile, 'w')
fout.write('# Third Party Blobs\n\n')
fout.write('This repository includes the following code from other projects.\n\n')

blobs = {}
for section in pkglist:
	if 'authfile' in section:
		curl_args = get_auth_info(section['authfile'], section['urlbase'])
		if not len(curl_args):
			sys.stderr.write('No Credentials for %s' % section['urlbase'])
			continue
	else:
		curl_args = []

	do_manifest = False
	if 'manifest' in section and section['manifest'] == True:
		do_manifest = True

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
		if do_manifest:
			create_manifest(manifest_dir, blobs[blob]['target'])

	for blob in sorted(blobs.keys()):
		fout.write('* %s [%s]\n' % (blob, blobs[blob]['source']))

fout.close()
