export ROLL		= stacki
export ROLLVERSION	= 5.0_$(shell date +%Y%m%d)

COLOR			= lightsteelblue
ISOSIZE			= 0

KICKSTART_LANG		= "en_US"
KICKSTART_LANGSUPPORT	= "en_US"

CODENAME		= WithGreatPower
export RELEASE		= $(shell $(STACKBUILD.ABSOLUTE)/bin/redhat-release)

BOOTABLE		= 0
ROLLS.OS		= redhat
