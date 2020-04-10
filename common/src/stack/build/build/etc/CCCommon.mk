# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ifndef __CCCOMMON_MK
__CCCOMMON_MK = yes

##
## Default RELEASE, official build process will override this
##

-include $(ROLLROOT)/version.mk
# try a little harder to get a symbolic reference out of git:
# print the first of the following:
#   symbolic-ref of HEAD on current branch (basically the branch name; most common)
#   a tag name associated with current commit (detached head state)
#   the abbreviated tag (detached head, no tag)
#   empty string (this isn't a git repo)
STACK	?= $(shell echo \
                   `git symbolic-ref -q --short HEAD  2>/dev/null || \
                    git describe --tags --exact-match 2>/dev/null || \
                    git rev-parse --short HEAD        2>/dev/null` | \
                    tr / _ | tr - _)
RELEASE	?= $(STACK)

##
## Brand all of our packages
##

COMPANY   = StackIQ
COPYRIGHT = (c) $(YEAR) $(COMPANY)
VENDOR    = $(COMPANY)

##
## Setup any_python.
## This lets some of our build scripts be written in a python2 and python3
## and scripts can use /usr/bin/env any_python for the shebang.
##
## This should run at parse time when make is run before any targets are run.
## This is put in this location so that building pallets will also set this up.
##
ANY_PYTHON = /usr/bin/any_python
#$(info CCCommon.mk is setting up any_python)
# If any_python is not already set up.
ifeq ($(shell which any_python),)
# Try to set it to python2 before setting it to python3.
ifneq ($(shell which python),)
#$(info symlinking $(shell which python) to $(ANY_PYTHON))
$(shell ln -s "$(shell which python)" $(ANY_PYTHON))
else ifneq ($(shell which python3),)
$(info symlinking $(shell which python3) to $(ANY_PYTHON))
$(shell ln -s "$(shell which python3)" $(ANY_PYTHON))
endif
# Else any_python is already set up.
else
#$(info any_python already set up)
endif

endif # __CCCOMMON_MK
