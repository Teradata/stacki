# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ROLLROOT	= ../../../../..

include $(STACKBUILD)/etc/CCRules.mk

EXTRACT := gunzip -c 

include images.mk
include ../../common/images.mk

install:: 
SHA = $(shell sha1sum sles-stacki.img | awk '{print "SHA1 "$$1;}')
