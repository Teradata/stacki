#!/bin/bash

# Bail on script errors
set -e

# Make sure we are passed an ISO to test
if [[ -z "$1" ]]
then
    echo "Usage: ./set-up.sh STACKI_ISO"
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
    source ../../bin/activate
fi

# Bring up the frontend
vagrant up frontend

# Install pytest-cov on the frontend
vagrant ssh frontend -c "sudo -i python3 -m ensurepip"
vagrant ssh frontend -c "sudo -i pip3 install pytest-cov"

# Output the ssh configuration from Vagrant for py.test to use
vagrant ssh-config frontend > ".cache/ssh-config"
