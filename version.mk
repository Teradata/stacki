export ROLL		= stacki
export ROLLVERSION	= 05.03.00.00
#export ROLLVERSION	= 5.0_$(shell date +%Y%m%d)_$(shell git rev-parse --short HEAD)
export RELEASE		= $(shell $(STACKBUILD.ABSOLUTE)/bin/os-release)

ISOSIZE			= 0

KICKSTART_LANG		= "en_US"
KICKSTART_LANGSUPPORT	= "en_US"
