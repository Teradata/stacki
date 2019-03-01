#!/bin/bash

# Bail on script errors
set -e

# The standard stacki Redhat 7 system test-suite gets a single ISO
if [[ "$#" -eq 1 && $1 =~ stacki-.*-redhat7\.x86_64\.disk1\.iso ]]
then
    # Start discovery
    vagrant ssh frontend -c "sudo -i stack enable discovery"

    # Bring up the backends a bit apart
    # Note: Vagrant Virtualbox provider doesn't support --parallel, so we do it here
    vagrant up backend-0-0 &
    sleep 10
    vagrant up backend-0-1 &
    wait

    # Wait until the frontend sees that backend-0-0 is online
    while [[ -z $(vagrant ssh frontend -c "sudo -i stack list host status backend-0-0 output-format=json | grep online") ]]
    do
        echo "Waiting for backend-0-0..."
        sleep 60
    done

    # And backend-0-1
    while [[ -z $(vagrant ssh frontend -c "sudo -i stack list host status backend-0-1 output-format=json | grep online") ]]
    do
        echo "Waiting for backend-0-1..."
        sleep 60
    done
fi
