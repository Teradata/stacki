# @copyright@
# @copyright@

PKGROOT		= /tftpboot/debian
ROLLROOT	= ../../../..

include $(STACKBUILD)/etc/CCRules.mk

ARCHS = amd64 arm64 armhf

deploy: install-pkg
	cp -R $(PKGROOT) /tftpboot

netboot: Makefile
	mkdir netboot
	cd netboot; for arch in $(ARCHS); do tar -xzf ../netboot-$$arch.tar.gz; done

build: netboot

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	cd netboot; find | cpio -pduv $(ROOT)/$(PKGROOT);

clean::
	-rm -rf netboot



