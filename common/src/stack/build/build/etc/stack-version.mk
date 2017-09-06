# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

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

# All docbook stuff include a publication date, let make this global
# right here.

PUBDATE = $(shell date +'%b %d %Y')
YEAR = $(shell date +'%Y')

rocks-copyright.txt:
	@rm -f $@
	@touch $@
	@echo '@Copyright@' >> $@
	@echo 'Copyright (c) 2000 - 2010 The Regents of the University of California' >> $@
	@echo 'All rights reserved. Rocks(r) v5.4 www.rocksclusters.org' >> $@
	@echo 'https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt' >> $@
	@echo '@Copyright@' >> $@
	-cat $@ | grep -v "^@Copyright" | expand -- > $@.tmp
	-mv $@.tmp $@


clean::
	@rm -f rocks-copyright.txt

endif
