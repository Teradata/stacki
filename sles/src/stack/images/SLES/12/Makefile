# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../../../..

include $(STACKBUILD)/etc/CCRules.mk

EXTRACT := xzcat

include ../../common/images.mk

install:: 
SHA = $(shell sha256sum sles-stacki.img | awk '{print "SHA256 "$$1;}')

clean::
	rm -rf cache
