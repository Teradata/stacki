#!/bin/bash

# Bail on script errors
set -e

# Make sure we are passed an ISO to test
if [[ -z "$1" ]]
then
    echo "Usage: ./set-up.sh STACKI_ISO [EXTRA_ISOS...]"
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

# Create the top level .cache directory and get a full path to it
CACHE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../"; pwd)/.cache"
if [[ ! -d "$CACHE_DIR" ]]
then
    mkdir "$CACHE_DIR"
fi

# Now process the extra ISOs
EXTRA_ISOS=()
while [[ "$#" -gt 0 ]]
do
    # Make sure that the EXTRA_ISO actually exists
    EXTRA_ISO="$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
    if [[ ! -f "$EXTRA_ISO" ]]
    then
        echo
        echo -e "\033[31mError: $EXTRA_ISO doesn't exist\033[0m"
        echo
        exit 1
    fi

    # Copy the EXTRA_ISO to the .cache directory, if needed
    if [[ "$(cd "$(dirname "$1")"; pwd)" != "$CACHE_DIR" ]]
    then
        $cp "$EXTRA_ISO" "$CACHE_DIR" 2>/dev/null
    fi

    # Add the filename EXTRA_ISOS array, which will be accessible
    # under /export/isos/ inside the frontend VM
    EXTRA_ISOS+=("$(basename "$EXTRA_ISO")")

    shift 1
done

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

# Run the set-up.d scripts
for SETUP_FILE in set-up.d/*
do
    if [[ -f $SETUP_FILE && -x $SETUP_FILE ]]
    then
        ./$SETUP_FILE $STACKI_ISO "${EXTRA_ISOS[@]}"
    fi
done

# Bring up the backends a bit apart
# Note: Vagrant Virtualbox provider doesn't support --parallel, so we do it here
vagrant up backend-0-0 &
sleep 10
vagrant up backend-0-1 &
wait
