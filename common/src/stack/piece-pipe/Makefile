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

PKGROOT		= /usr/sbin
ROLLROOT	= ../../..
DEPENDS.FILES	= $(wildcard *.c)

include $(STACKBUILD)/etc/CCRules.mk

CPPFLAGS	= -DVERSION="\"$(VERSION)\""
EXECS		= csp draino detour detach


build: $(EXECS)

csp: csp.o
	$(CC) $(CFLAGS) -o$@ $^

draino: draino.o
	$(CC) $(CFLAGS) -o$@ $^

detour: detour.o
	$(CC) $(CFLAGS) -o$@ $^

detach: detach.o
	$(CC) $(CFLAGS) -o$@ $^


install::
	mkdir -p $(ROOT)/$(PKGROOT)
	$(INSTALL) -m755 $(EXECS) $(ROOT)/$(PKGROOT)


clean::
	rm -f *.o $(EXECS)

