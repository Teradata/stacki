# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


def str2bool(s):
	"""
	Converts an on/off, yes/no, true/false string to True/False.

	Booleans will be returned as they are, as will non-boolean False-y values.

	Anything else must be a string.
	"""
	if type(s) == bool:
		return s
	if s and s.upper() in [ 'ON', 'YES', 'Y', 'TRUE', '1' ]:
		return True
	else:
		return False


def bool2str(b):
	"""
	Converts an 1/0, True/False to a yes/no

	Non integer and non boolean values will be returned as None

	"""
	if type(b) in [ bool, int ]:
                if b:
                        return 'yes'
                else:
                        return 'no'
	return None
