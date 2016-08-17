export ROLL		= stacki
export ROLLVERSION	= 3.3

COLOR			= lightsteelblue
BOOTABLE		= 1
ISOSIZE			= 0

KICKSTART_LANG		= "en_US"
KICKSTART_LANGSUPPORT	= "en_US"

CODENAME		= PetaData
export RELEASE		= $(shell $(STACKBUILD.ABSOLUTE)/bin/redhat-release)

