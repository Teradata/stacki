export ROLL		= stacki
export ROLLVERSION	= 4.0_$(shell date +%Y%m%d)

COLOR			= lightsteelblue
ISOSIZE			= 0

KICKSTART_LANG		= "en_US"
KICKSTART_LANGSUPPORT	= "en_US"

CODENAME		= WithGreatPower
export RELEASE		= $(shell $(STACKBUILD.ABSOLUTE)/bin/redhat-release)

