# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
# 
# A central makefile (Stack wide) to specify the version of
# Python we are using.
#
# Unlike version.mk variables, this can be used by both Ganglia,
# contrib, and Stack packages.
#

ifndef __PYTHON_MK
__PYTHON_MK = yes

PY.VERSION	= 3.7
PY.PATH		= /opt/stack/bin/python3
PY.LIB		= python$(PY.VERSION)
PY.STACK	= /opt/stack/lib/$(PY.LIB)/site-packages/
PY.TEST		= /opt/stack/bin/py.test

.PHONY: test
test:
	$(PY.TEST)  $(PY.TEST.FLAGS) -v tests

clean::
	@if [ -d tests ]; then 					\
		rm -rf tests/__pycache__;			\
		find tests -name *.pyc -exec rm -f {} \;;	\
	fi


endif	#__PYTHON_MK
