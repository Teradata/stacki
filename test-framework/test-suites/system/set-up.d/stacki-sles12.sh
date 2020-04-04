#!/bin/bash

# Bail on script errors
set -e

# The standard stacki SLES12 system test-suite gets a single ISO
if [[ "$#" -eq 1 && $1 =~ stacki-.*-sles12\.x86_64\.disk1\.iso ]]
then
    # Start discovery
    vagrant ssh frontend --no-tty -c "sudo -i stack enable discovery"

    # Bring up the backends (120 minute timeout)
    ./set-up.d/_common.sh 120
fi
