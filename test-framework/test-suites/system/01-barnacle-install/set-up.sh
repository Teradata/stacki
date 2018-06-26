#!/bin/bash

# Bail on script errors
set -e

# Make sure we are passed an ISO to test
if [[ -z "$1" ]]
then
    echo "Usage: ./set-up.sh STACKI_ISO EXTRA_ISOS..."
    exit 1
fi

# Make sure that the ISO actually exists
if [[ ! -f "$1" ]]
then
    echo
    echo -e "\033[31mError: $1 doesn't exist\033[0m"
    echo
    exit 1
fi

# Get the full path to the ISO
STACKI_ISO="$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
shift 1

# This test also accepts a SLES11 Stacki ISO as the EXTRA ISO, see if we got one
STACKI_SLES11_ISO=""
while [[ "$#" -gt 0 ]]
do
    # Is this our SLES11 iso?
    if [[ $(basename "$1") =~ stacki-.*-sles11\.x86_64\.disk1\.iso ]]
    then
        STACKI_SLES11_ISO="$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
    fi

    shift 1
done

# If we got a SLES11 Stacki ISO, make sure it exists
if [[ -n "$STACKI_SLES11_ISO" && ! -f "$STACKI_SLES11_ISO" ]]
then
    echo
    echo -e "\033[31mError: $STACKI_SLES11_ISO doesn't exist\033[0m"
    echo
    exit 1
fi

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

# Create the local test's .cache folder, if needed
if [[ ! -d .cache ]]
then
    mkdir .cache
fi

# Write out the Vagrant state info
cat > ".cache/state.json" <<EOF
{
    "STACKI_ISO": "$STACKI_ISO",
    "PLAYBOOK": "provisioning/barnacled-frontend.yml",
    "NAME": "test-framework-$(printf '%04x%04x' $RANDOM $RANDOM)",
    "TESTS": "$PWD/tests",
    "TEST_FILES": "$PWD/test-files"
}
EOF

# Make sure we have the virtualenv activated
if [[ -z $VIRTUAL_ENV ]]
then
    source ../../../bin/activate
fi

# Bring up the frontend
vagrant up frontend

# Set up the SLES11 box if we got that ISO passed in
if [[ -n "$STACKI_SLES11_ISO" ]]
then
    # Download the SLES11 ISO if it isn't already in the cache
    cd ../../../.cache
    if [[ ! -f "SLES-11-SP3-DVD-x86_64-GM-DVD1.iso" ]]
    then
        echo
        echo -e "\033[34mDownloading SLES-11-SP3-DVD-x86_64-GM-DVD1.iso ...\033[0m"
        curl -f --progress-bar -O "http://stacki-builds.labs.teradata.com/installer-isos/SLES-11-SP3-DVD-x86_64-GM-DVD1.iso"
    fi
    cd - >/dev/null

    # Make the sles11sp3 box on the frontend
    vagrant ssh frontend -c "sudo -i stack add box sles11sp3"

    # Add the SLES11 pallet to the box
    vagrant ssh frontend -c "sudo -i stack add pallet /export/isos/SLES-11-SP3-DVD-x86_64-GM-DVD1.iso"
    vagrant ssh frontend -c "sudo -i stack enable pallet SLES version=11.3 box=sles11sp3"

    # Add the SLES11 Stacki ISO to the box
    vagrant ssh frontend -c "sudo -i stack add pallet /export/isos/$(basename $STACKI_SLES11_ISO)"
    vagrant ssh frontend -c "sudo -i stack enable pallet stacki release=sles11 box=sles11sp3"

    # Add the vagrant cart to the box
    vagrant ssh frontend -c "sudo -i stack enable cart vagrant box=sles11sp3"
    
    # Start discovery
    vagrant ssh frontend -c "sudo -i stack enable discovery box=sles11sp3 installaction='install sles 11.3'"
else
    # Start discovery
    vagrant ssh frontend -c "sudo -i stack enable discovery"
fi

# Bring up the backends a bit apart
# Note: Vagrant Virtualbox provider doesn't support --parallel, so we do it here
vagrant up backend-0-0 &
sleep 10
vagrant up backend-0-1 &
wait

# Output the ssh configuration from Vagrant for py.test to use
vagrant ssh-config > ".cache/ssh-config"
