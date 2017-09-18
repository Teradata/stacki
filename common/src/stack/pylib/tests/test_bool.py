# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.bool import str2bool, bool2str


def test_str2bool():

	for true in [ 'yes', 'true', 'on', '1' ]:
		assert str2bool(true)

	for false in [ 'no', 'false', 'off', '0' ]:
		assert not str2bool(false)


def test_bool2str():
	assert bool2str(True)  == 'yes'
	assert bool2str(False) == 'no'
