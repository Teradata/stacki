# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

ifndef __RELEASE_MK
__RELEASE_MK = yes

ifeq ($(ROLLVERSION),)
VERSION	= $(shell /opt/stack/bin/stack report version)
else
VERSION	= $(ROLLVERSION)
endif

STACK_VERSION = $(VERSION)
# A name, not a RPM release id. Added for flair. First releases named
# after well-known mountains.

RELEASE_NAME = 7.x
VERSION_NAME = "$(RELEASE_NAME)"

# The project name is used to identify to distribution.  The base 
# distribution is controlled by the "stack" projects.  If you want to
# build you own distribution and differentiate it from the parent
# distribution change this variable.  This is used by the anaconda
# loader as an attribute on the URL kickstart request line.

PROJECT_NAME = stack

endif
