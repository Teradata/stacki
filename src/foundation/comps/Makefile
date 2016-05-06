#
# @SI_Copyright@
# @SI_Copyright@
#

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= comps.xml
DISTVERSION	= $(shell stack report version)
RPM.ARCH	= noarch

include $(STACKBUILD)/etc/CCRules.mk

build: 

install::
	mkdir -p $(ROOT)/RedHat/base
	install -ma+r comps.xml $(ROOT)/RedHat/base

