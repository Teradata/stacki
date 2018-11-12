# @SI_Copyright@
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.DIRS	= stack

include $(STACKBUILD)/etc/CCRules.mk

build:

install:: build
	mkdir -p $(ROOT)/$(PY.STACK)/stack
	(								\
		cd stack;						\
		find . -name "*.py" | 					\
			cpio -pduv $(ROOT)/$(PY.STACK)/stack;		\
	)
#	$(PYTHON) -mcompileall $(ROOT)/$(PY.STACK)
#	find $(ROOT)/$(PY.STACK)/ -name "*.py" -exec rm {} \;

clean::
	find stack -name *.pyc -exec rm -f {} \;
