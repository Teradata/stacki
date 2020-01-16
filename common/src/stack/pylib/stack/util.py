#! /opt/stack/bin/python
#
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
import shlex
import itertools
import tarfile
from xml.sax import handler
from pathlib import Path
import re

# An exception for Kickstart builder trinity: kcgi, kgen, kpp


class KickstartError(Exception):
	pass


class KickstartGraphError(KickstartError):
	pass


class KickstartNodeError(KickstartError):
	pass

# Simulate 'C' struct, but in Pythons funky dynamic way e.g.:
#
#	foo = Stuct()
#	foo.bar = 1
#	foo.oof = foo.bar
#
# cool, huh?


class Struct:
	pass


def flatten(items):
	''' flatten a nested list of items
	[(a,), (b,)]        -> [a, b]
	[(a,), (b,) (c, d)] -> [a, b, c, d]
	'''
	return list(itertools.chain.from_iterable(items))


def _exec(cmd, *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', shlexsplit=False, **kwargs):
	if shlexsplit:
		cmd = shlex.split(cmd)
	return subprocess.run(cmd, **kwargs, stdout=stdout, stderr=stderr, encoding=encoding)


def listcmp(l1, l2):
	return map(lambda a, b: a == b, l1, l2)


def list_isprefix(l1, l2):
	l = listcmp(l1, l2)
	for i in range(0, len(l1)):
		if not l[i]:
			return 0
	return 1


def getNativeArch():
	"""Returns the canotical arch as reported by the operating system"""

	arch = os.uname()[4]
	if arch in [ 'i386', 'i486', 'i586', 'i686']:
		arch = 'i386'
	return arch


def mkdir(newdir):
	"""Works the way a good mkdir should :)
		- already exists, silently complete
		- regular file in the way, raise an exception
		- parent directory(ies) does not exist, make them as well
		From Trent Mick's post to ASPN."""
	if os.path.isdir(newdir):
		pass
	elif os.path.isfile(newdir):
		raise OSError("a file with the same name as the desired dir, '%s', already exists." %
			      newdir)
	else:
		head, tail = os.path.split(newdir)
		if head and not os.path.isdir(head):
			mkdir(head)
		if tail:
			os.mkdir(newdir)



class ParseXML(handler.ContentHandler,
	       handler.DTDHandler,
	       handler.EntityResolver,
	       handler.ErrorHandler):
	"""A helper class to for XML parsers. Uses our
	startElement_name style."""

	def __init__(self, app=None):
		handler.ContentHandler.__init__(self)
		self.app = app
		self.text = ''


	def startElement(self, name, attrs):
		"""The Mason Katz school of parsers. Make small functions
		instead of monolithic case statements. Easier to override and
		to add new tag handlers."""
		try:
			f = getattr(self, "startElement_%s" % name)
			f(name, attrs)
		except AttributeError:
			return


	def endElement(self, name):
		try:
			f = getattr(self, "endElement_%s" % name)
			f(name)
		except AttributeError:
			return


	def characters(self, s):
		self.text += s


def system(cmd):
	print(cmd)
	return os.system(cmd)


def blank_str_to_None(string):
	if isinstance(string, str) and string.strip() == '':
		return None

	return string

def unique_everseen(iterable, key=None):
	"""List unique elements, preserving order. Remember all elements ever seen.

	unique_everseen('AAAABBBCCDAABBB') --> A B C D
	unique_everseen('ABBCcAD', str.lower) --> A B C D

	Source: https://docs.python.org/3/library/itertools.html#itertools-recipes
	"""
	seen = set()
	seen_add = seen.add
	if key is None:
		for element in itertools.filterfalse(seen.__contains__, iterable):
			seen_add(element)
			yield element
	else:
		for element in iterable:
			k = key(element)
			if k not in seen:
				seen_add(k)
				yield element

def lowered(iterable):
	"""Return a generator that lowercases all strings in the provided iterable."""
	return (string.lower() for string in iterable)

def is_valid_hostname(name):
	"""Check if a given name is a valid hostname.

	For our purposes, a valid hostname is a single hostname label (or "name")
	as defined by RFCs 952 and 1123. That is, a name of 1 to 63 characters
	starting and ending with a letter or digit and having letters, digits,
	and/or hyphens in between.
	"""
	return bool(
		re.match(
			r"""
			# <let-or-digit>
			^[a-z0-9]$
			# / <let-or-digit> 0*61<let-or-digit-or-hyphen> <let-or-digit>
			|^[a-z0-9][a-z0-9\-]{0,61}[a-z0-9]$
			""",
			name,
			flags=re.IGNORECASE | re.VERBOSE
		)
	)

def copy_remote_file(file_path, dest_path, dest_host, uncompress = True, uncompress_file_name = ''):
		"""
		Transfer over a file to a given host and optionally uncompress it.

		If uncompressed_file_name is set, it will not overwrite the file on disk
		if it exists at the destination path. Handles compressed gzip2 or tar archives.
		By setting the uncompress_file_name argument, if a file exists at the destination
		path, it will not be overwritten.

		Raises IOError or OSError when an action could not be completed.
		"""

		if not Path(file_path).is_file():
			raise OSError(f'File {file_path} not found to transfer')

		transfer_file = Path(file_path)
		dest = Path(dest_path)

		# Path for of the files final path name
		# used to check if a file with the same name
		# is present
		final_file_path = Path(f'{dest}/{uncompress_file_name}')

		# Path to transferred file location
		copy_file_path = Path(f'{dest}/{transfer_file.name}')

		# Create the path on the host
		create_dest = _exec(f'ssh {dest_host} "mkdir -p {dest}"', shlexsplit=True)
		if create_dest.returncode != 0:
			raise OSError(f'Could not create file folder {dest} on {dest_host}:\n{create_dest.stderr}')

		# Check if the file already exists at the given location
		if uncompress_file_name:
			file_present = _exec(f'ssh {dest_host} "ls {final_file_path}"', shlexsplit=True)
			if file_present.returncode == 0:
				return

		# Transfer the file
		copy_file = _exec(f'scp {transfer_file} {dest_host}:{dest}', shlexsplit=True)
		if copy_file.returncode != 0:
			raise OSError(f'Failed to transfer file {transfer_file} to {dest_host} at {copy_file_path}:\n{copy_file.stderr}')

		# Use tar to uncompress the file if it's in a tarfile
		if tarfile.is_tarfile(copy_file_path) and uncompress:
			untar = _exec(f'ssh {dest_host} "tar -xvf {copy_file_path} -C {dest} && rm {copy_file_path}"', shlexsplit=True)
			if untar.returncode != 0:
				raise OSError(f'Failed to unpack file archive {transfer_file.name} on {dest_host}:\n{untar.stderr}')

		# Otherwise use gunzip if its compressed using gzip
		elif copy_file_path.name.endswith('.gz') and uncompress:
			unzip = _exec(f'ssh {dest_host} "gunzip {copy_file_path}"', shlexsplit=True)
			if unzip.returncode != 0:
				raise OSError(f'Failed to unpack file {transfer_file} on {dest_host}:\n{unzip.stderr}')

def remove_remote_file(remove_file, host):
		"""
		Remove a file on the specified host
		at the given path

		Raise a FileNotFoundError if the remote file isn't
		present

		Raise an OSError if the remote file couldn't
		be removed
		"""

		file_path = Path(remove_file)
		file_present = _exec(f'ssh {host} "ls {file_path}"', shlexsplit=True)
		if file_present.returncode != 0:
			raise OSError(f'Could not find file {file_path.name} on {host}')
		rm_file_out = _exec(f'ssh {host} "rm {file_path}"', shlexsplit=True)
		if rm_file_out.returncode != 0:
			raise OSError(f'Failed to remove file {file_path.name}:{rm_file_out.stderr}')
