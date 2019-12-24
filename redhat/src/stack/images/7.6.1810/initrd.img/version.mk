ORDER			= 99
PKGROOT			= /opt/stack/images
OVERLAY.PKGS = \
	glibc-common
OVERLAY.UPDATE.PKGS	= \
	MegaCLI storcli \
	foundation-python \
	ludicrous-speed \
	stack-command \
	stack-probepal \
	stack-pylib \
	foundation-newt \
	foundation-python-Flask \
		foundation-python-itsdangerous \
		foundation-python-Werkzeug \
		foundation-python-Click \
		foundation-python-MarkupSafe \
		foundation-python-Jinja2 \
	foundation-python-PyMySQL \
	foundation-python-configparser \
	foundation-python-jsoncomment \
	foundation-python-python-daemon \
	foundation-python-lockfile \
	foundation-python-requests \
	foundation-python-urllib3 \
	foundation-python-chardet \
	foundation-python-certifi \
	foundation-python-six \
	foundation-python-idna

