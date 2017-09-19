# @copyright@
# Copyright (c) 2006 - 2017 Teradata
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


endif # __CCCOMMON_MK
