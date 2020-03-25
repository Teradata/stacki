# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

TEMPDIR := $(shell mktemp -d)

PALLET_PATCH_DIR = /opt/stack/pallet-patches/$(SUSE_PRODUCT)-$(IMAGE_VERSION)-$(IMAGE_RELEASE)-$(DISTRO_FAMILY)-$(ARCH)
#PALLET_PATCH_DIR = /opt/stack/$(SUSE_PRODUCT)-pallet-patches/$(IMAGE_VERSION)/$(IMAGE_RELEASE)

-include ../../../common/images-$(OS).mk

# In sles < 15 the checksum file is called `content`, but in sles >= 15 (at this time)
# the file is called `CHECKSUMS`.
ifeq ($(RELEASE),sles15)
CHECKSUMS_FILE = CHECKSUMS
else
CHECKSUMS_FILE = content
endif

dirs:
	@mkdir -p $(CURDIR)/sles-stacki

rpminst: localrepo getpackages getextrapackages
	rpm --dbpath $(TEMPDIR) -ivh --nodeps --force --badreloc \
		--relocate=/=$(CURDIR)/sles-stacki $(RPMLOC)
	rm -rf $(TEMPDIR)

sles-stacki.img: dirs rpminst
	@echo "Building sles-stacki.img"
	# Patch the sles-stacki image
	-(cd ../../../common/sles-stacki.img-patches && \
		(find . -type f  | cpio -pudv ../../$(SUSE_PRODUCT)/$(IMAGE_RELEASE)/$(IMAGE_VERSION)/sles-stacki/) )
	-(cd sles-stacki.img-patches && (find . -type f | cpio -pudv ../../../sles-stacki/) )
	# Create a squash filesystem
	mksquashfs $(CURDIR)/sles-stacki $@


stacki-initrd.img:
	@echo "Building $(SUSE_PRODUCT) initrd"
	mkdir -p stacki-initrd
	$(EXTRACT) initrd | ( cd stacki-initrd ; cpio -iudcm )
ifeq ($(RELEASE),sles15)
	# Under SLES 15's newer version of gpg we need to wire up the agent sockets to a different location
	printf '%%Assuan%%\nsocket=/dev/shm/S.gpg-agent\n' > ~/.gnupg/S.gpg-agent
	printf '%%Assuan%%\nsocket=/dev/shm/S.gpg-agent.browser\n' > ~/.gnupg/S.gpg-agent.browser
	printf '%%Assuan%%\nsocket=/dev/shm/S.gpg-agent.extra\n' > ~/.gnupg/S.gpg-agent.extra
	printf '%%Assuan%%\nsocket=/dev/shm/S.gpg-agent.ssh\n' > ~/.gnupg/S.gpg-agent.ssh
endif
	gpg --no-default-keyring --keyring stacki-initrd/installkey.gpg \
		--import ../../../common/gnupg-keys/stacki.pub
	rm -rf stacki-initrd/installkey.gpg~
	# Add common patches to initrd
	-(cd ../../../common/initrd-patches && \
		(find . -type f  | cpio -pudv ../../$(SUSE_PRODUCT)/$(IMAGE_RELEASE)/$(IMAGE_VERSION)/stacki-initrd/) )
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
	$(INSTALL) -m0644 linux $(ROOT)/$(PKGROOT)/vmlinuz-$(shell echo $(SUSE_PRODUCT) | tr A-Z a-z)-$(IMAGE_RELEASE)-${IMAGE_VERSION}-$(ARCH)
	$(INSTALL) -m0644 stacki-initrd.img $(ROOT)/$(PKGROOT)/initrd-$(shell echo $(SUSE_PRODUCT) | tr A-Z a-z)-$(IMAGE_RELEASE)-${IMAGE_VERSION}-$(ARCH)
	# Copy over patch files
	mkdir -p $(ROOT)/$(PALLET_PATCH_DIR)/add-stacki-squashfs
	cd SLES-pallet-patches && (find . -type f | cpio -pudv $(ROOT)/$(PALLET_PATCH_DIR)/add-stacki-squashfs)
	$(INSTALL) -m0644 sles-stacki.img $(ROOT)/$(PALLET_PATCH_DIR)/add-stacki-squashfs/boot/x86_64/sles-stacki.img
	# Add the HASH of the stacki image to the CHECKSUMS_FILE
	echo "$(SHA)  boot/x86_64/sles-stacki.img" >> $(ROOT)/$(PALLET_PATCH_DIR)/add-stacki-squashfs/$(CHECKSUMS_FILE)
	# Sign the content file
	gpg --armor \
		--output $(ROOT)/$(PALLET_PATCH_DIR)/add-stacki-squashfs/$(CHECKSUMS_FILE).asc \
		--detach-sig $(ROOT)/$(PALLET_PATCH_DIR)/add-stacki-squashfs/$(CHECKSUMS_FILE)

clean::
	rm -rf $(CURDIR)/localrepo
	rm -rf $(CURDIR)/localdir.repo
	rm -rf $(CURDIR)/stacki
	rm -rf $(CURDIR)/sles-stacki.img
	rm -rf $(CURDIR)/stacki-initrd
	rm -rf $(CURDIR)/stacki-initrd.img
	rm -rf $(CURDIR)/sles-stacki
