# @SI_Copyright@
# @SI_Copyright@

ROLLROOT = .

-include $(ROLLSBUILD)/etc/CCRolls.mk

local:
	mkdir -p build-$(ROLL)-$(STACK)/RPMS
	cp -r ../common/build-$(ROLL)-$(STACK)/RPMS/* \
		build-$(ROLL)-$(STACK)/RPMS/
	echo
	make roll

common:
	(cd ../common ; make roll)

pallet: common local
	echo
	echo "building stacki pallet, CentOS edition"
	echo


