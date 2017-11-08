#!/bin/bash

command -v getarg >/dev/null || . /lib/dracut-lib.sh

info "STACKIQ: init"

[ ! -h /opt ] && ln -s /updates/opt /opt

# Setup ld.conf for /opt/stack/lib (python3 needs this)
if [ ! -f /etc/ld.so.conf ]; then
echo "include ld.so.conf.d/*.conf" > /etc/ld.so.conf
fi

echo /opt/stack/lib > /etc/ld.so.conf.d/stacki.conf

ldconfig
