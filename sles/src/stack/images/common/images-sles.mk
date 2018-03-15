RPMLOC = $(shell find cache -type f -name *.rpm)

localrepo:
	mkdir -p $(CURDIR)/localrepo
	@echo $(CURDIR)/../../../../../RPMS
	@echo $(REDHAT.ROOT)
	ln -s $(CURDIR)/../../../../../RPMS $(CURDIR)/localrepo 
	createrepo $(CURDIR)/localrepo
	@echo -e "[localdir] \n\
name=local \n\
baseurl=file://$(CURDIR)/localrepo\n\
assumeyes=1 \n\
gpgcheck=0 \n\
enabled=1" > localdir.repo

getpackages: localrepo
	rm -rf cache
	mkdir -p cache
	zypper --pkg-cache-dir cache download $(YUMLIST.SLES)
	zypper --pkg-cache-dir cache --reposd-dir $(CURDIR) clean --all
	zypper --pkg-cache-dir cache --reposd-dir $(CURDIR) download $(YUMLIST.STACK)

