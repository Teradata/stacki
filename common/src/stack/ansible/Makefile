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

	# Install the callback plugin
	mkdir -p $(ROOT)/opt/stack/ansible/plugins/callback
	$(INSTALL) -m0644 plugins/callback/failure_report.py $(ROOT)/opt/stack/ansible/plugins/callback/

	# Install the module_utils plugin
	mkdir -p $(ROOT)/opt/stack/ansible/plugins/module_utils
	$(INSTALL) -m0644 plugins/module_utils/stacki.py $(ROOT)/opt/stack/ansible/plugins/module_utils/

	# Install the modules
	mkdir -p $(ROOT)/opt/stack/ansible/plugins/modules
	$(INSTALL) -m0644 plugins/modules/stacki_box_info.py $(ROOT)/opt/stack/ansible/plugins/modules/

clean::
