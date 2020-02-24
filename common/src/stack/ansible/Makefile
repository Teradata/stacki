# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


ROLLROOT = ../../../..
include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	# Copy over our custom Ansible config
	mkdir -p $(ROOT)/opt/stack/etc/
	$(INSTALL) -m0644 etc/ansible.cfg $(ROOT)/opt/stack/etc/ansible.cfg

	# Install the inventory plugin
	mkdir -p $(ROOT)/opt/stack/ansible/plugins/inventory
	$(INSTALL) -m0644 plugins/inventory/stacki.py $(ROOT)/opt/stack/ansible/plugins/inventory/

clean::
