#
# Do not edit
#

.PHONY: install-rpm
install-rpm: /export/src/stacki/common/src/stack/hwtest/iperf/../../../build--master/RPMS/x86_64/iperf3-5.0_20171011_28bfe24-master.x86_64.rpm
	rpm -Uhv --force --nodeps $<
