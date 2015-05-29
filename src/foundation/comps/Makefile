#
# @SI_Copyright@
# @SI_Copyrighr@
#

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= comps.xml
DISTVERSION	= $(shell stack report version)
RPM.ARCH	= noarch

include $(STACKBUILD)/etc/CCRules.mk

bootstrap:	rpm
	-mkdir -p /export/stack/contrib/default/$(DISTVERSION)/x86_64/RPMS
	-cp ../../../build-cluster-core*/RPMS/noarch/foundation-comps* \
		/export/stack/contrib/default/$(DISTVERSION)/x86_64/RPMS

build: 

install::
	mkdir -p $(ROOT)/RedHat/base
	install -ma+r comps.xml $(ROOT)/RedHat/base

