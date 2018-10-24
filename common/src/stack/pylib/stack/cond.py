#! /opt/stack/bin/python
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


from collections import UserDict


class _CondEnv(UserDict):
	"""This is a special dictionary that rather than throwing
	an exception when an item is not found it just returns None.  It is
	used to create a special local() environment where all unresolved
	variables evaluate to None.  This allows condintional expressions
	that refer to non-existent attributes to evaluate to False."""
	
	def __getitem__(self, key):

		# print '__getitem__', key
		
		# Handle boolean special since they are not in the
		# environment

		if key.lower() == 'true':
			return True
		if key.lower() == 'false':
			return False
		
		try:
			val = UserDict.__getitem__(self, key)
		except:
			return None	# undefined vars are None

		try:
			if val.lower() in [ 'on', 'true', 'yes', 'y' ]:
				return True
			if val.lower() in [ 'off', 'false', 'no', 'n' ]:
				return False
		except:
			pass

		# Everything else is returned as a string

		return val
		

def CreateCondExpr(archs, oses, releases, cond):
	"""Build a boolean expression from the old Rocks style
	arch, os, and release conditionals along with the new style
	generic cond XML tag attribute.

	ARCHS	 = comma separated list of architectures
	OSES	 = comma separated list of oses
	RELEASES = comma separated list of stacki releases
	COND	 = boolean expression in Python syntax

	The resulting expression string is the AND and all the above, where
	the ARCHS, OSES, and RELEASES are also ORed.

	The purposes is to build a single Python expression that can
	evaluate the old style "arch=", "os=", "release=" attributes along
	with the new generic "cond=" attributes.  The means that the following
	XML tags are equivalent:

	<edge from="foo" to="base" arch="i386"/>
	<edge from="foo" to="base" cond="arch=='i386'"/>
	"""

	exprs = []
    
	if archs:
		list = []		# OR of architectures
		for arch in archs.string(','):
			list.append('arch=="%s"' % arch.strip())
		exprs.append("( %s )" % ' or '.join(list))

	if oses:
		list = []		# OR of OSes
		for os in oses.split(','):
			list.append('os=="%s"' % os.strip())
		exprs.append("( %s )" % ' or '.join(list))

	if releases:
		list = []		# OR of releases
		for release in releases.split(','):
			list.append('release=="%s"' % release.strip())
		exprs.append("( %s )" % ' or '.join(list))

	if cond:
		exprs.append(cond)	# AND of the above and the generic cond

	return ' and '.join(exprs)


    
def EvalCondExpr(cond, attrs):
	"""Tests the conditional expression.  The ATTRS dictionary is use to
	build the Python local() dictional (local vars) and the COND
	expression is evaluated in using these variables.  In other words,
	for every key-value pair in the ATTRS dictionary a Python variable
	is created, this allows the COND expression to directly refer to
	all the attributes as variables.
	"""
	if not cond:
		return True

	cond = cond.replace('.', '_DOT_')

	env = _CondEnv()
	for (k, v) in attrs.items():
		if v is None:
			continue

		# FIXME
		#
		# list.attr:addHostAttrs we create [] attributes instead of strings
		# catch when this happens and replace the '.' to '_DOT_' in the
		# list elements.
		#
		# This is horrible, but fixes the code for now. Will open a ticket
		# to clean this up.

		if type(v) == type([]):
			l = [ ]
			for s in v:
				l.append(s.replace('.', '_DOT_'))
			v = l
		else:
			v = v.replace('.', '_DOT_')
		k = k.replace('.', '_DOT_')
#		print(cond, ':', k, ':', v)
		env[k] = v

	try:
		result = eval(cond, globals(), env)
	except:
		result = False

	return result
