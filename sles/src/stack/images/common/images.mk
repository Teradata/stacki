# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

TEMPDIR := $(shell mktemp -d)

PALLET_PATCH_DIR = /opt/stack/$(SUSE_PRODUCT)-pallet-patches/$(IMAGE_VERSION)/$(IMAGE_RELEASE)

-include ../../../common/images-$(OS).mk

dirs:
	@mkdir -p $(CURDIR)/sles-stacki

rpminst: localrepo getpackages getextrapackages
	rpm --dbpath $(TEMPDIR) -ivh --nodeps --force --badreloc \
		--relocate=/=$(CURDIR)/sles-stacki $(RPMLOC)
	rm -rf $(TEMPDIR)

sles-stacki.img: dirs rpminst
	@echo "Building sles-stacki.img"
	# SymLink /usr/bin/python to foundation-python
	mkdir -p $(CURDIR)/sles-stacki/usr/bin
	ln -s /opt/stack/bin/python3 $(CURDIR)/sles-stacki/usr/bin/python
	# Patch the sles-stacki image
	-(cd ../../../common/sles-stacki.img-patches && \
		(find . -type f  | cpio -pudv ../../$(SUSE_PRODUCT)/$(IMAGE_VERSION)/$(IMAGE_RELEASE)/sles-stacki/) )
	-(cd sles-stacki.img-patches && (find . -type f | cpio -pudv ../../../sles-stacki/) )
	# Create a squash filesystem
	mksquashfs $(CURDIR)/sles-stacki $@


stacki-initrd.img:
	@echo "Building $(SUSE_PRODUCT) initrd"
	mkdir -p stacki-initrd
	$(EXTRACT) initrd | ( cd stacki-initrd ; cpio -iudcm ) 
	gpg --no-default-keyring --keyring stacki-initrd/installkey.gpg \
		--import ../../../common/gnupg-keys/stacki.pub
	rm -rf stacki-initrd/installkey.gpg~
	# Add common patches to initrd
	-(cd ../../../common/initrd-patches && \
		(find . -type f  | cpio -pudv ../../$(SUSE_PRODUCT)/$(IMAGE_VERSION)/$(IMAGE_RELEASE)/stacki-initrd/) )
	# Add version specific patches to initrd
	-(cd initrd-patches && \
		(find . -type f  | cpio -pudv ../stacki-initrd/) )
	# Pack it up
	(				\
		cd stacki-initrd;	\
		find . | cpio -oc | gzip -c - > ../stacki-initrd.img; \
	)

keyring:
	gpg --batch --import ../../../common/gnupg-keys/stacki.pub
	gpg --batch --import ../../../common/gnupg-keys/stacki.priv

build: sles-stacki.img stacki-initrd.img


install:: keyring
	mkdir -p $(ROOT)/$(PKGROOT)
	$(INSTALL) -m0644 linux $(ROOT)/$(PKGROOT)/vmlinuz-$(shell echo $(SUSE_PRODUCT) | tr A-Z a-z)-$(IMAGE_VERSION)-${IMAGE_RELEASE}-$(ARCH)
	$(INSTALL) -m0644 stacki-initrd.img $(ROOT)/$(PKGROOT)/initrd-$(shell echo $(SUSE_PRODUCT) | tr A-Z a-z)-$(IMAGE_VERSION)-${IMAGE_RELEASE}-$(ARCH)
	# Copy over patch files
	mkdir -p $(ROOT)/$(PALLET_PATCH_DIR)
	cd $(SUSE_PRODUCT)-pallet-patches && (find . -type f | cpio -pudv $(ROOT)/$(PALLET_PATCH_DIR))
	$(INSTALL) -m0644 sles-stacki.img $(ROOT)/$(PALLET_PATCH_DIR)/boot/x86_64/sles-stacki.img
	# Add the SHA1 of the stacki image to content file
	echo "HASH $(SHA)  boot/x86_64/sles-stacki.img" >> $(ROOT)/$(PALLET_PATCH_DIR)/content
	# Sign the content file
	gpg --armor \
		--output $(ROOT)/$(PALLET_PATCH_DIR)/content.asc \
		--detach-sig $(ROOT)/$(PALLET_PATCH_DIR)/content

clean::
	rm -rf $(CURDIR)/localrepo
	rm -rf $(CURDIR)/localdir.repo
	rm -rf $(CURDIR)/stacki
	rm -rf $(CURDIR)/sles-stacki.img
	rm -rf $(CURDIR)/stacki-initrd
	rm -rf $(CURDIR)/stacki-initrd.img
	rm -rf $(CURDIR)/sles-stacki
