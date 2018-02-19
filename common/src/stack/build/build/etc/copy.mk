nuke::
	for rpmfile in *.rpm; do				\
		arch=`rpm -qp --queryformat "%{ARCH}" $$rpmfile`;\
		rm -rf $(REDHAT.RPMS)/$$arch/$$rpmfile;		\
	done

rpm::
	for rpmfile in *.rpm; do				\
		arch=`rpm -qp --queryformat "%{ARCH}" $$rpmfile`;\
		mkdir -p $(REDHAT.RPMS)/$$arch/;		\
		cp -p $$rpmfile $(REDHAT.RPMS)/$$arch/;		\
	done

install-rpm:: rpm
	for rpmfile in *.rpm; do				\
		arch=`rpm -qp --queryformat "%{ARCH}" $$rpmfile`;\
		rpm -Uhv --force --nodeps $(REDHAT.RPMS)/$$arch/$$rpmfile; \
	done

