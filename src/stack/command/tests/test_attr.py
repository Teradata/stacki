# @SI_Copyright@
#                             www.stacki.com
#                                  v3.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

import pytest
import random
import stack
from stack.bool import *
from stack.api import *

HOST	    = 'backend-1000-0'
ENVIRONMENT = 'pytest'


def setup_module(module):
        Call('add host %s' % HOST)
        Call('set host attr %s attr=environment value=%s' % (HOST, ENVIRONMENT))
        Call('set environment attr %s attr=key value=value' % ENVIRONMENT)

def teardown_module(module):
        Call('remove host %s' % ENVIRONMENT)


def test_attr(table=None, owner=None):
	"""
	Tests the Scoping rules for attributes.  Called without
	arguments this test the global attributes.
	
	table = os | appliance | host
	owner = osname | appliancename | hostname
	"""

	if not table:
		table = ''
	if not owner:
		owner = ''

	result = Call('remove %s attr' % table, ('%s attr=a.b.c.d' % owner).split())
	assert ReturnCode() == 0 and result == [ ]

	for (key, (scope, attr)) in [ ('a.b.c.d', ('a.b.c', 'd')),
				      ('a/b.c.d', ('a', 'b.c.d')),
				      ('a.b/c.d', ('a.b', 'c.d')),
				      ('a.b.c/d', ('a.b.c', 'd')) ]:

		value = str(random.randint(0, 100))

		result = Call('set %s attr' % table,
			      ('%s attr=%s value=%s' % (owner, key, value)).split())
		assert ReturnCode() == 0 and result == [ ]

		if key != 'a.b.c.d':
			result = Call('list %s attr' % table,
				      ('%s attr=%s' %
				       (owner, key.replace('/', '.'))).split())
			assert ReturnCode() == 0 and len(result) == 1
			assert result[0]['scope'] == scope
			assert result[0]['attr']  == attr
			assert result[0]['value'] == value

		result = Call('list %s attr' % table,
			      ('%s attr=%s' % (owner, key)).split())

		assert ReturnCode() == 0 and len(result) == 1
		assert result[0]['scope'] == scope
		assert result[0]['attr']  == attr
		assert result[0]['value'] == value


		result = Call('remove %s attr' % table,
		      ('%s attr=a.b.c.d' % owner).split())
	assert ReturnCode() == 0 and result == [ ]

	
def test_os_attr():
	test_attr('os', 'redhat')

def test_environment_attr():
        test_attr('environment', ENVIRONMENT)
        
def test_appliance_attr():
	test_attr('appliance', 'backend')
	test_attr('appliance', 'frontend')

def test_host_attr():
	test_attr('host', HOST)
