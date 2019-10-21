YUMLIST = \
	MegaCLI storcli \
	ludicrous-speed \
	stack-command \
	stack-mq \
	stack-probepal \
	stack-pylib \
	stack-storage-config 

getextrapackages:
	cp RPMS/*rpm cache/
	zypper --pkg-cache-dir cache download ipmitool
