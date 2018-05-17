#!/bin/bash

# Bail on script errors
set -e

# Make sure we are passed a frontend ISO to test
if [[ -z "$1"  ]]
then
    echo "Usage: ./set-up.sh STACKI_ISO ADDITIONAL_ISO"
    exit 1
fi

# Make sure we are passed an additional ISO to test
if [[ -z "$2" ]]
then
    echo "Usage: ./set-up.sh STACKI_ISO ADDITIONAL_ISO"
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

# Make sure that the ISO actually exists
if [[ ! -f "$2" ]]
then
    echo
    echo -e "\033[31mError: $2 doesn't exist, not testing SLES 11 \033[0m"
    echo
fi

if [[ $(basename "$1") =~ stacki-.*-sles12\.x86_64\.disk1\.iso ]]; then
    # This test also accepts a SLES11 Stacki ISO as the EXTRA ISO, see if we got one
    # But only if we were passed a sles12 front end. Skip extra isos for RHEL or other frontends
    STACKI_SLES11_ISO=""
    while [[ "$#" -gt 0 ]]
    do
        # Is this our SLES11 iso?
        if [[ $(basename "$1") =~ stacki-.*-sles11\.x86_64\.disk1\.iso ]]; then
            STACKI_SLES11_ISO="$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
        fi

        shift 1
    done
else
    echo
    echo -e "\033[31mError: Currently only support SLES 12 and SLES 12 + 11 partitioning testing.\033[0m"
    echo
    if [[ -f ".cache/state.json" ]]; then
        rm ".cache/state.json"
    fi
    exit 0
fi


# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

# Create the local test's .cache folder, if needed
if [[ ! -d .cache ]]
then
    mkdir .cache
fi

randomize_name=$(printf '%04x%04x' $RANDOM $RANDOM)

# Write out the Vagrant state info
cat > ".cache/state.json" <<EOF
{
    "STACKI_ISO": "$STACKI_ISO",
    "SLES_11_STACKI_ISO": "$STACKI_SLES11_ISO",
    "PLAYBOOK": "provisioning/barnacled-frontend.yml",
    "NAME": "test-framework-$randomize_name",
    "TESTS": "$PWD/tests",
    "BACKENDS":  ["backend-0-0", "backend-0-1", "backend-0-2", "backend-0-3", "backend-0-4", "backend-0-5"]
}
EOF

# Bring up the frontend
vagrant up frontend

# Output the ssh configuration from Vagrant for py.test to use
vagrant ssh-config frontend > ".cache/ssh-config"

# Start discovery
vagrant ssh frontend -c "sudo -i stack enable discovery"

# Bring up the backends a bit apart
# Note: Vagrant Virtualbox provider doesn't support --parallel, so we do it here
set +e
vagrant up backend-0-0 &
sleep 10
vagrant up backend-0-1 &
sleep 10
vagrant up backend-0-2 &
sleep 10
vagrant up backend-0-3 &
sleep 10
vagrant up backend-0-4 &
sleep 10
vagrant up backend-0-5 &
wait
sleep 10
vagrant halt --force backend-0-0 &
sleep 10
vagrant halt --force backend-0-1 &
sleep 10
vagrant halt --force backend-0-2 &
sleep 10
vagrant halt --force backend-0-3 &
sleep 10
vagrant halt --force backend-0-4 &
sleep 10
vagrant halt --force backend-0-5 &
wait
sleep 10
set -e

# Start discovery
vagrant ssh frontend -c "sudo -i stack disable discovery"
