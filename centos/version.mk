export ROLL		= stacki
export ROLLVERSION	= 5.0

COLOR			= lightsteelblue
ISOSIZE			= 0

KICKSTART_LANG		= "en_US"
KICKSTART_LANGSUPPORT	= "en_US"

CODENAME		= WithGreatPower
export RELEASE		= $(shell $(STACKBUILD.ABSOLUTE)/bin/os-release)

BOOTABLE		= 0
ROLLS.OS		= redhat
