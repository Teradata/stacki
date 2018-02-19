# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import time


def DoNotEdit(prefix='# '):
	"""Return standard warning to generated files"""

	t = [ '',
              'WARNING: This file is generated do not edit.',
              '',
	      'Contents last written on %s by Stacki.' % time.strftime('%D %T %p'),
	      '' ]

	s = ''
	for line in t:
		s += '%s%s\n' % (prefix, line)
	return s

	
