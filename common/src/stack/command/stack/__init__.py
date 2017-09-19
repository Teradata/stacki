# This file is used only in the source code (not installed) to allow
# the developer to run ./stack.py locally and use the local command
# and pylib source code before using the system installed code.  This
# means you can/should/must run (and test) the command line before
# installing the RPM.
#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os

__path__.append(os.path.join(os.path.split(__file__)[0], '..', '..', 'pylib', 'stack'))
__path__.append('/opt/stack/lib/python3.6/site-packages/stack')

version = 'no-version'
release = 'no-release'
