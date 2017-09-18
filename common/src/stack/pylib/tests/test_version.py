# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack


def test_version():
	"""
	Make sure stack.version is undefined which means we are
	running against pylib/stack and not the system libraries.
	"""

	assert stack.version == 'no-version'
	assert stack.release == 'no-release'

	
