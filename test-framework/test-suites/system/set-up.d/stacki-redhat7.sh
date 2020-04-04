#!/bin/bash

# Bail on script errors
set -e

# The standard stacki Redhat 7 system test-suite gets a single ISO
if [[ "$#" -eq 1 && $1 =~ stacki-.*-redhat7\.x86_64\.disk1\.iso ]]
then
    # Load hostfile and set partitioning for backend-0-0 and backend-0-1
    vagrant ssh frontend --no-tty -c "sudo -i /export/test-suites/system/files/set-redhat-host-partitions.sh"

    # Start discovery
    vagrant ssh frontend --no-tty -c "sudo -i stack enable discovery"

    # Bring up the backends (120 minute timeout)
    ./set-up.d/_common.sh 120
fi
