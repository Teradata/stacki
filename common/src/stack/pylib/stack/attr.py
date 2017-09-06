#! /opt/stack/bin/python
#
# Code for handling the new conditional attributes for both the graph
# edges and nodes.
#
# The old style arch/os/release attributes are still supported in the
# new code.
#
# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import string

def NormalizeAttr(attr):
	"""Takes a fully-scoped attribute and returns a string
	that can be used as and XML entity or displaying in the
	list commands.  In other words, it converts any '/'
	delimeter into a scoping '.' character.
	"""
	(s, a) = SplitAttr(attr)
	return ConcatAttr(s, a)

	
def SplitAttr(attr):
	"""Takes a fully-scoped attributed and returns a tuple of the
	(scope, attr).  If there is no scope it returns (None, attr).
	"""

	s = ''
	a = ''

	if attr:
		if attr.find('/') >= 0:
			tokens = attr.split('/')
		else:
			tokens = attr.rsplit('.', 1)
		if len(tokens) == 1:
			a = attr
		else:
			if tokens[1]:
				s = tokens[0]
				a = tokens[1]
			else:
				s = tokens[0]

	return (s, a)


def ConcatAttr(scope, attr, slash=False):
	"""Combine the SCOPE and ATTR to give the canonical name of
	the attribute."""

	if scope:
		if slash:
			sep = '/'
		else:
			sep = '.'
		return '%s%s%s' % (scope, sep, attr)
	return attr

	
