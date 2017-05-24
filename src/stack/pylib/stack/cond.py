#! /opt/stack/bin/python
#
# @SI_Copyright@
# @SI_Copyright@
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@


import string
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
		
		# Handle boolean special since there are not in the
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
		try:
			return int(val)
		except ValueError:
			pass

		# Try to convert value to a float
		try:
			return float(val)
		except ValueError:
			pass

		# Try to convert value to a boolean
		
		if val.lower() in [ 'on', 'true', 'yes', 'y' ]:
			return True
		if val.lower() in [ 'off', 'false', 'no', 'n' ]:
			return False

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
		for arch in string.split(archs, ','):
			list.append('arch=="%s"' % arch.strip())
		exprs.append("( %s )" % string.join(list,' or '))

	if oses:
		list = []		# OR of OSes
		for os in string.split(oses, ','):
			list.append('os=="%s"' % os.strip())
		exprs.append("( %s )" % string.join(list,' or '))

	if releases:
		list = []		# OR of releases
		for release in string.split(releases, ','):
			list.append('release=="%s"' % release.strip())
		exprs.append("( %s )" % string.join(list,' or '))

	if cond:
		# Make into a legal python variable by replace the scope ('.')
		# operator with _DOT_.  The eval needs to do the same thing.
		exprs.append(cond)	# AND of the above and the generic cond

	return string.join(exprs, ' and ')


    
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
	cond = cond.replace('!=', ' is not ')

	env = _CondEnv()
	for (k,v) in attrs.items():
		env[k.replace('.', '_DOT_')] = v
		
	# print 'EvalCondExpr', cond
	result = eval(cond, globals(), env)

	return result
