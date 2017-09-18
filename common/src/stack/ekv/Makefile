# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

LIB		= lib
CPPFLAGS	= -DVERSION="\"$(VERSION)\""
MAKE.rpmflag	= -bb --define "__spec_install_post :"
ROLLROOT	= ../../..
DEPENDS.FILES	= $(wildcard *.c) $(wildcard *.py)

include $(STACKBUILD)/etc/CCRules.mk
include $(STACKBUILD)/etc/python.mk

build:	make-bootable-disks make-unbootable-disks check_port

make-bootable-disks: make-bootable-disks.o
	$(CC) $(CFLAGS) -o$@ $^

make-unbootable-disks: make-unbootable-disks.o
	$(CC) $(CFLAGS) -o$@ $^

#
# add the system utilities which ekv needs and are not provided
# in the standard red hat installation
#
install::
	mkdir -p $(ROOT)/opt/stack/bin/
	cp /bin/stty $(ROOT)/opt/stack/bin/

	mkdir -p $(ROOT)/usr/$(LIB)

	#
	# python files to support the pseudo tty
	#
	mkdir -p $(ROOT)/usr/sbin
	$(INSTALL) -m755 pty-wrapper.py $(ROOT)/usr/sbin/

	#
	# executable that makes sure all disks are 'bootable'
	#
	cp make-bootable-disks $(ROOT)/opt/stack/bin/
	cp make-unbootable-disks $(ROOT)/opt/stack/bin/

	cp check_port $(ROOT)/opt/stack/bin/


clean::
	rm -f *.o $(EXECS) make-bootable-disks make-unbootable-disks check_port

