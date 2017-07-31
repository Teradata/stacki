# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

from __future__ import print_function
import os
import time
import pytest
from stack.api import *

NUMRACKS    = 1
RACKSIZE    = 1
ENVIRONMENT = 'pytest'

def setup_module(module):
	Call('add environment %s' % ENVIRONMENT)
	for rack in range(1000, 1000 + NUMRACKS):
		for rank in range(0, RACKSIZE):
			host = 'backend-%d-%d' % (rack, rank)
			Call('add host %s environment=%s' % (host, ENVIRONMENT))

	Call('set environment attr %s attr=key value=value' % ENVIRONMENT)

	result = Call('list host %s' % ENVIRONMENT)
	assert ReturnCode() == 0 and len(result) == (NUMRACKS * RACKSIZE)

			
def teardown_module(module):
	Call('remove host %s' % ENVIRONMENT)
	Call('remove environment %s' % ENVIRONMENT)


def test_scale():
	print('...')
	t0 = time.time()
	Call('list host')
	t1 = time.time()
	print('list host (%.3fs)' % (t1-t0))
	t0 = time.time()
	Call('list host profile', [ 'backend-1000-0' ])
	t1 = time.time()
	print('list host profile (%.3fs)' % (t1-t0))
	




