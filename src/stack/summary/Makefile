# @SI_Copyright@
# @SI_Copyright@
#

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.DIRS	= stack

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	mkdir -p $(ROOT)/$(PY.STACK)/stack
	(								\
		cd stack;						\
		find . -name "*.py" | 					\
			cpio -pduv $(ROOT)/$(PY.STACK)/stack;		\
	)
	find $(ROOT)/$(PY.STACK)/stack/ -name "*.py" | gawk		\
		'{ print "\nRollName = \"$(ROLL)\"" >> $$1; }'  

clean::
	find stack -name *.pyc -exec rm -f {} \;
