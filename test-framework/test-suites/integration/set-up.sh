#!/bin/bash

# Bail on script errors
set -e

# Parse the command line
USE_SRC=0
ISO=""
while [[ "$#" -gt 0 ]]
do
    case "$1" in
        --use-src)
            USE_SRC=1
            shift 1
            ;;
        *)
            ISO="$1"
            shift 1
            ;;
    esac
done

# Make sure we are passed an ISO to test
if [[ -z "$ISO" ]]
then
    echo "Usage: ./set-up.sh [--use-src] STACKI_ISO"
    exit 1
fi

# See if we need to download the ISO
if [[ $ISO =~ https?:// ]]
then
    # Make sure we are in the project directory
    cd "$(dirname "${BASH_SOURCE[0]}")"

	# Create the local test's .cache folder, if needed
	if [[ ! -d .cache ]]
	then
		mkdir .cache
	fi

    # Download the ISO if needed
    cd .cache
    if [[ ! -f "$(basename "$ISO")" ]]
    then
        echo
        echo -e "\033[34mDownloading $(basename "$ISO") ...\033[0m"
        curl -f --progress-bar -O "$ISO"
    fi

	# Get the full path to the ISO
	STACKI_ISO="$(pwd)/$(basename "$ISO")"

    # Move back up to the project root
    cd ..
else
	# Make sure that the ISO actually exists
	if [[ ! -f "$ISO" ]]
	then
		echo
		echo -e "\033[31mError: $ISO doesn't exist\033[0m"
		echo
		exit 1
	fi

	# Get the full path to the ISO
	STACKI_ISO="$(cd "$(dirname "$ISO")"; pwd)/$(basename "$ISO")"

	# Make sure we are in the same directory as this script
	cd "$(dirname "${BASH_SOURCE[0]}")"

	# Create the local test's .cache folder, if needed
	if [[ ! -d .cache ]]
	then
		mkdir .cache
	fi
fi

# Make sure a few folders needed by Vagrantfile exist
if [[ ! -d "../../reports" ]]
then
    mkdir "../../reports"
fi

if [[ ! -d "../../.cache" ]]
then
    mkdir "../../.cache"
fi

# Write out the Vagrant state info
cat > ".cache/state.json" <<EOF
{
    "STACKI_ISO": "$STACKI_ISO",
    "PLAYBOOK": "provisioning/barnacled-frontend.yml",
    "NAME": "test-framework-$(printf '%04x%04x' $RANDOM $RANDOM)",
    "TESTS": "$PWD/tests",
    "TEST_FILES": "$PWD/test-files",
	"USE_SRC": "$USE_SRC"
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
