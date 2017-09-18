#! /opt/stack/bin/python
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


try:
	from UserDict import UserDict
except ImportError:
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

		# Try to convert value to an integer
#		try:
#			return int(val)
#		except ValueError:
#			pass

		# Try to convert value to a float
#		try:
#			return float(val)
#		except ValueError:
#			pass

		# Try to convert value to a boolean
		
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

	ARCHS	= comma separated list of architectures
	OSES	= comma separated list of oses
	RELEASES	= command separated list of Rocks releases
	COND	= boolean expression in Python syntax

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
		# Make into a legal python variable by replace the scope ('.')
		# operator with _DOT_.	The eval needs to do the same thing.
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
	cond = cond.replace('&&', ' and ')
	cond = cond.replace('||', ' or ')

	env = _CondEnv()
	for (k, v) in attrs.items():
		env[k.replace('.', '_DOT_')] = v
		
	# print 'EvalCondExpr', cond
	result = eval(cond, globals(), env)

	return result
