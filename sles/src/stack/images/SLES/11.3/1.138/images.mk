YUMLIST = MegaCLI storcli \
		stack-command \
		stack-pylib	\
		stack-storage-config \
		ludicrous-speed

getextrapackages:
	cp RPMS/*rpm cache/
	zypper --pkg-cache-dir cache download ipmitool
