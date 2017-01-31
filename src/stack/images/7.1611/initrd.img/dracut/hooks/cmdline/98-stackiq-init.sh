#!/bin/bash

command -v getarg >/dev/null || . /lib/dracut-lib.sh

info "STACKIQ: init"

[ ! -h /opt ] && ln -s /updates/opt /opt

