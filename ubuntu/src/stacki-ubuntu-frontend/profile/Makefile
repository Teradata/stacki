# @SI_Copyright@
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= $(wildcard *.py)


include $(STACKBUILD)/etc/CCRules.mk


build:

install::
	mkdir -p $(ROOT)/export/stack/sbin/profile
	$(INSTALL) -m 0755 ubuntu.py  $(ROOT)/export/stack/sbin/profile/

