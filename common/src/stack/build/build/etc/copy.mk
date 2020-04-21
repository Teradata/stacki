nuke::
	for rpmfile in *.rpm; do				\
		arch=`rpm -qp --queryformat "%{ARCH}" $$rpmfile 2> /dev/null`;\
		rm -rf $(REDHAT.RPMS)/$$arch/$$rpmfile;		\
	done

rpm::
	for rpmfile in *.rpm; do				\
		arch=`rpm -qp --queryformat "%{ARCH}" $$rpmfile 2> /dev/null`;\
		mkdir -p $(REDHAT.RPMS)/$$arch/;		\
		cp -p $$rpmfile $(REDHAT.RPMS)/$$arch/;		\
	done

install-rpm:: rpm
	for rpmfile in *.rpm; do				\
		arch=`rpm -qp --queryformat "%{ARCH}" $$rpmfile 2> /dev/null`;\
		rpm -Uv --force --nodeps $(REDHAT.RPMS)/$$arch/$$rpmfile; \
	done

