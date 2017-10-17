# This file is called from the generated spec file.
# It can also be used to debug rpm building.
# 	make -f .buildenv-/iperf3.spec.mk build|install

ifndef __RULES_MK
build:
	make ROOT=/export/src/stacki/common/src/stack/hwtest/iperf/iperf3.buildroot build

install:
	make ROOT=/export/src/stacki/common/src/stack/hwtest/iperf/iperf3.buildroot install
	/opt/stack/share/build/bin/genfilelist iperf3 /export/src/stacki/common/src/stack/hwtest/iperf/iperf3.buildroot > /tmp/iperf3-fileslist
endif
