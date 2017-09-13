# @SI_Copyright@
# @SI_Copyright@

ROLLROOT   = .

-include $(ROLLSBUILD)/etc/CCRolls.mk

.PHONY: 3rdparty
3rdparty:
	$(ROLLSBUILD)/bin/get3rdparty.py

bootstrap:: 3rdparty
	# Install package sets here
	# individual bootstrap requirement go in package
	# makefiles using the bootstrap-suse tag
	#
	# E.g. (From RedHat)
	#yum group install -y "Development Tools"
	#yum group install -y "Infrastructure Server"
	#yum install -y createrepo genisoimage emacs
	$(MAKE) -C ../common $@

common:
	make -C ../common rpms

preroll:: common
	mkdir -p build-$(ROLL)-$(STACK)/RPMS
	cp -r ../common/build-$(ROLL)-$(STACK)/RPMS/* build-$(ROLL)-$(STACK)/RPMS/
