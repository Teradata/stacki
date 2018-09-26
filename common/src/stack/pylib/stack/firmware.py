import hashlib
from pathlib import Path
import uuid
from urllib.parse import urlparse
import stack.download

# Base path to store managed firmware files under
BASE_PATH = Path('/export/stack/firmware/')
# Supported schemes to fetch firmware from a source to be managed by stacki
SUPPORTED_SCHEMES = ('file', 'http', 'https')
# Require the supported hash algorithms to be the always present ones
SUPPORTED_HASH_ALGS = hashlib.algorithms_guaranteed
# Attribute names used by the firmware commands to determine actions
MAKE_ATTR = 'component.make'
MODEL_ATTR = 'component.model'
FIRMWARE_ATTR = 'component.firmware'

class FirmwareError(Exception):
	"""The exception type raised by the firmware utilities in this module."""
	pass

def calculate_hash(file_path, hash_alg, hash_value = None):
	"""Calculates the hash of the provided file using the provided algorithm and returns it as a hex string.

	hash_alg is required to be one of the SUPPORTED_HASH_ALGS and a FirmwareError will be raised if it is not.

	If a hash value is provided, this checks the calculated hash against the provided hash. The hash_value should
	be a string of the form provided by hash.hexdigest(). A FirmwareError is raised if the hashes do not match.
	"""
	if hash_alg not in SUPPORTED_HASH_ALGS:
		raise FirmwareError(
			f'hash_alg must be one of the following: {SUPPORTED_HASH_ALGS}'
		)

	calculated_hash = hashlib.new(name = hash_alg, data = Path(file_path).read_bytes()).hexdigest()
	# check the hash if one was provided to check against
	if hash_value is not None and hash_value != calculated_hash:
		raise FirmwareError(
			f'Calculated hash {calculated_hash} does not match expected hash {hash_value}. Algorithm was {hash_alg}.'
		)

	return calculated_hash

def fetch_firmware(source, make, model, filename = None, **kwargs):
	"""Fetches the firmware file from the provided source and copies it into a stacki managed file.

	source should be the URL from which to pull the firmware image from. If this is not one of the
	supported schemes, a FirmwareError is raised.

	make and model must be set to the make and model the firmware image applies to.

	filename is the optional file name to write the image out to locally. This does not change the
	destination folder, only the file name.

	The remaining kwargs will be captured and passed through as necessary to the underlying mechanism
	used to fetch the file from the source. For example, fetching via HTTP might need a username and
	a password for authentication.

	A FirmwareError is raised if fetching the file from the source fails.
	"""
	# parse the URL to figure out how we're going to fetch it
	url = urlparse(url = source)

	# build file path to write out to
	dest_dir = BASE_PATH / make / model
	dest_dir = dest_dir.resolve()
	dest_dir.mkdir(parents = True, exist_ok = True)
	# set a random file name if the name is not set
	final_file = dest_dir / (uuid.uuid4().hex if filename is None else filename)

	# copy from local file
	if url.scheme == SUPPORTED_SCHEMES[0]:
		# grab the source file and copy it into the destination file
		try:
			source_file = Path(url.path).resolve(strict = True)
		except FileNotFoundError as exception:
			raise FirmwareError(f'{exception}')

		final_file.write_bytes(source_file.read_bytes())
	# download via HTTP/HTTPs
	elif url.scheme == SUPPORTED_SCHEMES[1] or url.scheme == SUPPORTED_SCHEMES[2]:
		try:
			stack.download.fetch(url = source, file_path = final_file, verbose = True, **kwargs)
		except stack.download.FetchError as exception:
			raise FirmwareError(f'{exception}')
	# add more supported schemes here
	# elif url.scheme == self.SUPPORTED_SCHEMES[N]:
	else:
		raise FirmwareError(
			f'source must use one of the following supported schemes: {SUPPORTED_SCHEMES}'
		)

	return final_file
