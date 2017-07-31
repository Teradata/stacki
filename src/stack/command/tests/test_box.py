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

def test_box():
	"""
	Test list/add/remove/set box.
	"""

	# Search for a unused box name and use it for
	# the following tests.

	done = False
	while not done:
		box = 'default-%s' % str(random.randint(0, 100))
		result = Call('list box', [ box ])
		if ReturnCode() and not result:
			done = True
	assert box

	# add box

	result = Call('add box', [ box ])
	assert ReturnCode() == 0 and result == []

	# lookup current box for host

	result = Call('list host', [ 'localhost' ])
	assert ReturnCode() == 0 and len(result) == 1
	prevBox = result[0]['box']

	# set box for this host

	result = Call('set host box', [ 'localhost', 'box=%s' % box ])
	assert ReturnCode() == 0

	# verify box was set

	result = Call('list host', [ 'localhost' ])
	assert ReturnCode() == 0 and len(result) == 1
	assert result[0]['box'] == box

	# restore prev setting

	result = Call('set host box', [ 'localhost', 'box=%s' % prevBox ])
	assert ReturnCode() == 0

	# remove box

	result = Call('remove box', [ box ])
	assert ReturnCode() == 0

	# try to remove default
	#	"remove box" should protect against this

	result = Call('remove box', [ 'default' ])
	assert ReturnCode() == 255

