# @SI_Copyright@
# @SI_Copyright@

YUMLIST = MegaCLI storcli hpssacli 	\
		stack-pylib		\
		foundation-python	\
		foundation-python-xml	\
		stack-command

LOCALYUMLIST = stacki-ubuntu-frontend-command \
		stacki-ubuntu-frontend-pylib

RPMLOC = $(wildcard ../../common/RPMS/*.rpm ./RPMS/*.rpm)
TEMPDIR := $(shell mktemp -d)
RPMLOC += $(shell repoquery --location $(YUMLIST))

dirs:
	@mkdir -p $(CURDIR)/ubuntu-stacki

rpminst:
	( \
	pwd; \
	for f in `ls ../../common/RPMS/*.rpm`; do	\
		cd $(CURDIR)/ubuntu-stacki; 	\
		rpm2cpio ../$$f | cpio -idum; \
	done; \
	)
	find $(CURDIR)/ubuntu-stacki -name '*.pyc' -exec rm -fr {} \;
	find $(CURDIR)/ubuntu-stacki -name '*.pyo' -exec rm -fr {} \;

debinst:
	( \
	pwd; \
	for f in `ls ../../common/PKGS`; do \
		dpkg-deb -x ../../common/PKGS/$$f ../../common/DEBS; \
	done; \
	)
	pwd;
	rsync -qlazup ../../common/DEBS/* $(CURDIR)/ubuntu-stacki/;

build: dirs rpminst debinst
	@echo "Building ubuntu-stacki.img"
	# SymLink /usr/bin/python to foundation-python
	mkdir -p $(CURDIR)/ubuntu-stacki/usr/bin
	ln -fs /opt/stack/bin/python $(CURDIR)/ubuntu-stacki/usr/bin/python
	ln -fs /usr/bin/vim.tiny $(CURDIR)/ubuntu-stacki/usr/bin/vi
	# Patch the ubuntu-stacki image
	-(cd ../../common/ubuntu-stacki.img-patches && \
		(find . -type f  | cpio -pud ../../$(UBUNTU_PRODUCT)/$(IMAGE_VERSION)/ubuntu-stacki/) )
	$(EXTRACT) initrd.gz | ( cd ubuntu-stacki; cpio -iudcm ) 
	(				\
		cd ubuntu-stacki;	\
		rm -f lib/libuuid* lib/libblkid* lib/libnl* lib/libgcrypt* lib/libgpg-error.so.0; \
		find . | cpio -oc | gzip -c - > ../ubuntu-stacki.img; \
	)

install::
	mkdir -p $(ROOT)/$(PKGROOT)
	$(INSTALL) -m0755 linux $(ROOT)/$(PKGROOT)/vmlinuz-ubuntu-$(shell echo $(UBUNTU_PRODUCT) | tr A-Z a-z)-$(IMAGE_VERSION)-$(ARCH)
	$(INSTALL) -m0644 ubuntu-stacki.img $(ROOT)/$(PKGROOT)/initrd-ubuntu-$(shell echo $(UBUNTU_PRODUCT) | tr A-Z a-z)-$(IMAGE_VERSION)-$(ARCH)

clean::
	rm -rf $(CURDIR)/localrepo
	rm -rf $(CURDIR)/localdir.repo
	rm -rf $(CURDIR)/stacki
	rm -rf $(CURDIR)/ubuntu-stacki.img
	rm -rf $(CURDIR)/ubuntu-stacki
	rm -rf ../../common/DEBS/*
