export ROLL		= stacki
export ROLLVERSION	= 5.0_$(shell date +%Y%m%d)_$(shell git rev-parse --short HEAD)
export RELEASE          = $(shell $(STACKBUILD.ABSOLUTE)/bin/os-release)

