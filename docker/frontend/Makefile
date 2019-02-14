.PHONY: build
build: Dockerfile barnacle.sh 
	(cd ../.. && docker build -f docker/frontend/Dockerfile -t stacki/frontend-centos:latest .)
