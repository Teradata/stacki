#!/bin/bash

# Bail on script errors
set -e

# The standard stacki SLES12 system test-suite gets a single ISO
if [[ "$#" -eq 1 && $1 =~ stacki-.*-sles12\.x86_64\.disk1\.iso ]]
then
    # Nothing to do but start discovery
    vagrant ssh frontend -c "sudo -i stack enable discovery"
fi
