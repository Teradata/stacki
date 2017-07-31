# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
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
	Call('add environment %s' % ENVIRONMENT)
	Call('set host environment %s environment=%s' % (HOST, ENVIRONMENT))
	Call('set environment attr %s attr=key value=value' % ENVIRONMENT)

def teardown_module(module):
	Call('remove host %s' % ENVIRONMENT)
	Call('remove environment attr %s attr=*' % ENVIRONMENT)
	Call('remove environment %s' % ENVIRONMENT)


def test_attr(table=None, owner=None):
	"""
	Tests the Scoping rules for attributes.  Called without
	arguments this test the global attributes.
	
	table = os | environment | appliance | host
	owner = osname | environmentname | appliancename | hostname
	"""

	if not table:
		table = ''
	if not owner:
		owner = ''

	attr   = 'a.b.c.d'
	result = Call('remove %s attr' % table, ('%s attr=%s' % (owner, attr)).split())
	assert ReturnCode() == 0 and result == [ ]

	value  = str(random.randint(0, 100))
	result = Call('set %s attr' % table,
		      ('%s attr=%s value=%s' % (owner, attr, value)).split())
	assert ReturnCode() == 0 and result == [ ]

	result = Call('list %s attr' % table, ('%s attr=%s' % (owner, attr)).split())
	assert ReturnCode() == 0 and len(result) == 1
	assert result[0]['attr']  == attr
	assert result[0]['value'] == value

	result = Call('remove %s attr' % table, ('%s attr=%s' % (owner, attr)).split())
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
