# @SI_Copyright@
# @SI_Copyright@

PKGROOT		= /opt/stack
ROLLROOT	= ../../..
DEPENDS.DIRS	= stack

include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	(								\
		cd stack;					        \
		find . -name "*.py" | 					\
			cpio -pduv $(ROOT)/$(PY.STACK)/stack;		\
	)
	find $(ROOT)/$(PY.STACK)/stack -name "*.py" | gawk		\
		'{ print "\nRollName = \"$(ROLL)\"" >> $$1; }'  
	$(PYTHON) -mcompileall $(ROOT)/$(PY.STACK)
	find $(ROOT) -type d -exec chmod a+rx {} \;

clean::
	find stack -name *.pyc -exec rm -f {} \;
