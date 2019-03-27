#!/bin/bash

# Bail on script errors
set -e

# The standard stacki SLES12 system test-suite gets a single ISO
if [[ "$#" -eq 1 && $1 =~ stacki-.*-sles12\.x86_64\.disk1\.iso ]]
then
    # Start discovery
    vagrant ssh frontend -c "sudo -i stack enable discovery"

    # Bring up the backends a bit apart
    # Note: Vagrant Virtualbox provider doesn't support --parallel, so we do it here
    vagrant up backend-0-0 &
    sleep 10
    vagrant up backend-0-1 &
    wait

    # Wait up to 5 minutes for the frontend to see that backend-0-0 is online (once Vagrant thinks they are up)
    for ((i = 0 ; i < 5 ; i++))
    do
        if [[ -z $(vagrant ssh frontend -c "sudo -i stack list host status backend-0-0 output-format=json | grep online") ]]
        then
            echo "Waiting for backend-0-0..."
            sleep 60
        else
            break
        fi
    done

    # Wait up to 5 minutes for the frontend to see that backend-0-1 is online (once Vagrant thinks they are up)
    for ((i = 0 ; i < 5 ; i++))
    do
        if [[ -z $(vagrant ssh frontend -c "sudo -i stack list host status backend-0-1 output-format=json | grep online") ]]
        then
            echo "Waiting for backend-0-1..."
            sleep 60
        else
            break
        fi
    done
fi
