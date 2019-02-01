include ../version.mk

.PHONY: build
build: Dockerfile barnacle.sh 
	(cd .. && docker build -f docker/Dockerfile -t stacki/frontend-centos:$(ROLLVERSION) .)
