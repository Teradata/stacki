# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
# if requests is not available,
# attempting to barnacle will fail
try:
	from urllib.parse import urlparse
	import requests
	from requests.auth import HTTPBasicAuth
except ImportError:
	pass

from stack.util import _exec

class FetchError(Exception):

	def __init__(self, message):
		self.message = message

	def __str__(self):
		return self.message


def fetch(url, username=None, password=None, verbose=False, file_path=None):
	filename = os.path.basename(urlparse(url).path)
	local_path = '/'.join([os.getcwd(), filename]) if file_path is None else file_path

	if username and password:
		s = requests.Session()
		s.auth = HTTPBasicAuth(username, password)
		r = s.get(url, stream=True)

	else:
		r = requests.get(url, stream=True)

	# verify that there are no http errors
	if r.status_code == 401:
		raise FetchError(f'unable to download {filename}: http error 401')
	if r.status_code == 404:
		raise FetchError(f'unable to download {filename}: http error 404')
	elif not r.ok:
		raise FetchError(f'unable to download {filename}, requests status code: {r.status_code}')

	# content length and progress will be used to provide a download progress indicator
	content_length = int(r.headers.get('content-length')) / 1000000
	progress = 0
	chunk_size = 1000000
	with open(local_path, 'wb') as f:
		for chunk in (item for item in r.iter_content(chunk_size=chunk_size) if item):
			f.write(chunk)
			f.flush()
			progress += 1
			if verbose:
				percent = int(progress/content_length * 100)
				print(f'{percent}%', end='\r')
		# watch out for premature connection closures by the download server
		# if the entire file has not been downloaded, don't pass an incomplete iso
		if progress < content_length:
			os.unlink(filename)
			raise FetchError(f'unable to download {filename}: the connection may have been prematurely closed by the server.\nFailed at {progress} MB out of {int(content_length)} MB')

	if verbose:
		print(f'success. downloaded {int(content_length)} MB.')

	return local_path

def fetch_artifact(url, dest_dir, username=None, password=None):
	'''
	fetch the artifact at `url` and write it to `dest_dir`. `dest_dir` must exist.
	if username and password are both defined, they will be used.
	if the server returns 401, 403, 404, or 500, or if curl exists non-zero (for eg connection errors), FetchError will be raised.
	'''

	curl_cmd = [
		'curl',
		'--write-out', '%{http_code}',   # send http status to stdout
		'--silent',                      # don't show download progress
		'--show-error',                  # kept for debugging purposes
		'--location',                    # follow redirects
		'--remote-name',                 # use the remote filename for the local filename
		'--retry', '3',
		'--config', '-',                 # get remaining config from STDIN (credentials)
		'--url',
		url,
	]

	creds = ''
	if username and password:
		creds = f'--user {username}:{password}'

	proc = _exec(curl_cmd, input=creds, cwd=dest_dir)

	http_codes = {
		'401': 'Unauthorized',
		'403': 'Forbidden',
		'404': 'Not Found',
		'500': 'Internal Server Error',
	}

	basic_error_msg = f"tried to run '{' '.join(proc.args)}'."

	if proc.returncode != 0:
		raise FetchError(f"{basic_error_msg}\n{proc.stderr}")

	if proc.stdout in http_codes:
		raise FetchError(f"{basic_error_msg}\nServer returned HTTP code {proc.stdout} - {http_codes[proc.stdout]}")
