BUILD_DIRS = insert-ethers

default: build

build::
	for i in $(BUILD_DIRS); do \
		cd $$i; make $@;\
	done;

install:
	for f in $(BUILD_DIRS); do \
	( cd $$f; make install; ) \
	done
