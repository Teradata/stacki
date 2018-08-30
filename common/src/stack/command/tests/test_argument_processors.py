# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.api import Call, ReturnCode

DNE = 'horse-with-no-name'

def test_name_does_not_exist():
	for o in [ 'appliance',
		   'box',
		   'cart',
		   'environment',
		   'host',
		   'network',
		   'os',
		   'pallet' ]:
		result = Call('list %s' % o, [ DNE ], stderr=False)
		assert ReturnCode() == 255











