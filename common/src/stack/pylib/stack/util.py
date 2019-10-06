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
from xml.sax import handler
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

def is_hostname_label(name):
	"""Check if a given name is a valid hostname label.

	Validity is defined by RFCs 952 and 1123.
	"""
	pattern = r"^[a-zA-Z0-9]$|^[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]$"
	return bool(re.match(pattern, name))
