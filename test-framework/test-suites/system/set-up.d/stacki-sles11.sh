#!/bin/bash

# Bail on script errors
set -e

# The standard Stacki SLES11 system test-suite gets two ISOs. The first
# is a SLES12 stacki ISO used for the frontend, and the second is the
# SLES11 stacki ISO.
if [[
    "$#" -eq 2 &&
    $1 =~ stacki-.*-sles12\.x86_64\.disk1\.iso &&
    $2 =~ stacki-.*-sles11\.x86_64\.disk1\.iso
]]
then
    # Download the SLES11 ISO if it isn't already in the cache
    cd ../../.cache
    if [[ ! -f "SLES-11-SP3-DVD-x86_64-GM-DVD1.iso" ]]
    then
        echo
        echo -e "\033[34mDownloading SLES-11-SP3-DVD-x86_64-GM-DVD1.iso ...\033[0m"
        curl -f --progress-bar -O "http://stacki-builds.labs.teradata.com/installer-isos/SLES-11-SP3-DVD-x86_64-GM-DVD1.iso"
    fi

    # We need the SDK ISO For SLES11 as well
    if [[ ! -f "SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso" ]]
    then
        echo
        echo -e "\033[34mDownloading SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso ...\033[0m"
        curl -f --progress-bar -O "http://stacki-builds.labs.teradata.com/installer-isos/SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso"
    fi
    cd - >/dev/null

    # Create the sles11sp3 box on the frontend
    vagrant ssh frontend -c "sudo -i /export/test-suites/system/files/create-sles11sp3-box.sh $2"

    # Start discovery
    vagrant ssh frontend -c "sudo -i stack enable discovery box=sles11sp3 installaction='install sles 11.3'"

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
