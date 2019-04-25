#!/bin/bash

# Bail on script errors
set -e

# The standard stacki Redhat 7 system test-suite gets a single ISO
if [[ "$#" -eq 1 && $1 =~ stacki-.*-redhat7\.x86_64\.disk1\.iso ]]
then
    # Start discovery
    vagrant ssh frontend -c "sudo -i stack enable discovery"

    # Bring up the backends (30 minute timeout)
    ./set-up.d/_common.sh 30
fi
