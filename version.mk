export ROLL		= stacki
export ROLLVERSION	= 4.0_$(shell date +%Y%m%d)

VERSION			= 4.0_$(shell date +%Y%m%d)

COLOR			= lightsteelblue
BOOTABLE		= 1
ISOSIZE			= 0

KICKSTART_LANG		= "en_US"
KICKSTART_LANGSUPPORT	= "en_US"

CODENAME		= PetaData
export RELEASE		= $(shell $(STACKBUILD.ABSOLUTE)/bin/redhat-release)

