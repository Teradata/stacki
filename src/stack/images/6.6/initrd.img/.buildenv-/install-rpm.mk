#
# Do not edit
#

.PHONY: install-rpm
install-rpm: /state/partition1/src/stacki/src/rocks/images/6.6/initrd/../../../build--develop/RPMS/x86_64/6.6-initrd-1.0-develop.x86_64.rpm
	rpm -Uhv --force --nodeps $<
