# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

ifndef __CCRULES_MK
__CCRULES_MK = yes

##
## Set default ROLL name
##
-include version.mk

##
## Load CCCommon.mk and Rocks Rules.mk
##
include $(STACKBUILD)/etc/CCCommon.mk
include $(STACKBUILD)/etc/Rules.mk

endif # __CCRULES_MK
