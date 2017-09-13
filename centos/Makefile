# @SI_Copyright@
# @SI_Copyright@

ROLLROOT   = .

-include $(ROLLSBUILD)/etc/CCRolls.mk

.PHONY: 3rdparty
3rdparty:
	$(ROLLSBUILD)/bin/get3rdparty.py

bootstrap:: 3rdparty
	yum group install -y "Development Tools"
	yum group install -y "Infrastructure Server"
	yum install -y createrepo genisoimage emacs
	$(MAKE) -C ../common $@

common:
	make -C ../common rpms

preroll:: common
	mkdir -p build-$(ROLL)-$(STACK)/RPMS
	cp -r ../common/build-$(ROLL)-$(STACK)/RPMS/* build-$(ROLL)-$(STACK)/RPMS/


#pallet: common local
#	echo
#	echo "building stacki pallet, CentOS edition"
#	echo


