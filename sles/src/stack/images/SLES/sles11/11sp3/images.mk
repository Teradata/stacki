YUMLIST = \
	MegaCLI storcli \
	ludicrous-speed \
	stack-command \
	stack-mq \
	stack-pylib \
	stack-storage-config \
	stack-graphql-api \
		foundation-python-ariadne \
			foundation-python-graphql-core \
			foundation-python-typing-extensions

getextrapackages:
	cp RPMS/*rpm cache/
	zypper --pkg-cache-dir cache download ipmitool
