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
import subprocess
#if requests is not available,
#attempting to barnacle will fail
try:
	from urllib.parse import urlparse
	import requests
	from requests.auth import HTTPBasicAuth
except:
	pass


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
	# determine how many digits long the size of the iso is so we can display a clean progress indicator
	content_digits = len(str(content_length))
	with open(local_path, 'wb') as f:
		for chunk in (item for item in r.iter_content(chunk_size=chunk_size) if item):
			f.write(chunk)
			f.flush()
			progress += 1
			if verbose == True:
				percent = int(progress/content_length * 100)
				print(f'{percent}%', end='\r')
		# watch out for premature connection closures by the download server
		# if the entire file has not been downloaded, don't pass an incomplete iso
		if progress < content_length:
			p = subprocess.run(['rm', filename])
			raise FetchError(f'unable to download {filename}: the connection may have been prematurely closed by the server.\nFailed at {progress} MB out of {int(content_length)} MB')

	if verbose == True:
		print(f'success. downloaded {int(content_length)} MB.')

	return local_path
