YUMLIST = \
	MegaCLI storcli \
	ipmitool \
	stack-checklist \
	stack-command \
	stack-mq \
	stack-pylib \
	stack-storage-config \
	ludicrous-speed \
	foundation-python \
	foundation-python-Flask \
		foundation-python-itsdangerous \
		foundation-python-Werkzeug \
		foundation-python-MarkupSafe \
		foundation-python-Jinja2 \
		foundation-python-Click \
	foundation-python-PyMySQL \
	foundation-python-configparser \
	foundation-python-jsoncomment \
	foundation-python-python-daemon \
		foundation-python-lockfile \
	foundation-python-requests \
		foundation-python-urllib3 \
		foundation-python-chardet \
		foundation-python-certifi \
		foundation-python-idna

# Under SLES 15, zypper download blows away the previous contents
# of the cache directory, so we need to download into a temp
# directory and then move the contents.
getextrapackages:
	rm -rf temp_cache
	mkdir -p temp_cache
	zypper --pkg-cache-dir temp_cache download ipmitool
	mv temp_cache/* cache/
	rm -rf temp_cache
