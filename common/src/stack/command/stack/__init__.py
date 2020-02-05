# This file is used only in the source code (not installed) to allow
# the developer to run ./stack.py locally and use the local command
# and pylib source code before using the system installed code.  This
# means you can/should/must run (and test) the command line before
# installing the RPM.
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import site

site_pkgs_path = [p for p in site.getsitepackages() if p.startswith('/opt/stack/lib/python')][0]

# Needed for use-the-src when symlinking pylib
# as its location differs in the package vs the src
# Related to https://bugs.python.org/issue17639
__path__.append(os.path.join(os.path.split(__file__)[0], '..', '..', 'pylib', 'stack'))
__path__.append(f'{site_pkgs_path}/stack')

version = 'no-version'
release = 'no-release'
