# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import random
from stack.api import Call, ReturnCode


def test_box():
	"""
	Test list/add/remove/set box.
	"""

	# Search for a unused box name and use it for
	# the following tests.

	done = False
	while not done:
		box = 'default-%s' % str(random.randint(0, 100))
		result = Call('list box', [ box ], stderr=False)
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

	result = Call('remove box', [ 'default' ], stderr=False)
	assert ReturnCode() == 255

	# remove multiple boxes
	# Add the first box back

	result = Call('add box', [ box ])
	assert ReturnCode() == 0 and result == []

	# get a second box name
	done = False
	while not done:
		second_box = 'default-%s' % str(random.randint(0, 100))
		result = Call('list box', [ second_box ], stderr=False)
		if ReturnCode() and not result:
			done = True
	assert second_box

	result = Call('add box', [ second_box ])
	assert ReturnCode() == 0 and result == []

	# remove multiple boxes

	result = Call('remove box', [ box, second_box ])
	assert ReturnCode() == 0
