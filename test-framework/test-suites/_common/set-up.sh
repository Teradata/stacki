#!/bin/bash

# Echo out the commands to the console
set -x

# Bail on script errors
set -e

# Create the top level .cache directory and get a full path to it
CACHE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../"; pwd)/.cache"
if [[ ! -d "$CACHE_DIR" ]]
then
    mkdir "$CACHE_DIR"
fi

# Parse the command line
USE_SRC=0
COVERAGE=0
ISO=""
EXTRA_ISOS=()

while [[ "$#" -gt 0 ]]
do
    case "$1" in
        --use-src)
            USE_SRC=1
            shift 1
            ;;
        --coverage)
            COVERAGE=1
            shift 1
            ;;
        *)
            # First ISO has to be our frontend
            if [[ -z "$ISO" ]]
            then
                ISO="$1"
            else
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
                    cp "$EXTRA_ISO" "$CACHE_DIR" 2>/dev/null
                fi

                # Add the filename EXTRA_ISOS array, which will be accessible
                # under /export/isos/ inside the frontend VM
                EXTRA_ISOS+=("$(basename "$EXTRA_ISO")")
            fi

            shift 1
            ;;
    esac
done

# Make sure we are passed an ISO to test
if [[ -z "$ISO" ]]
then
    echo "Usage: ./set-up.sh [--use-src] STACKI_ISO [EXTRA_ISOS...]"
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
	"USE_SRC": "$USE_SRC"
}
EOF

# Make sure we have the virtualenv activated
if [[ -z $VIRTUAL_ENV ]]
then
    source ../../bin/activate
fi

# Don't bother catching errors from this point on
set +e

# Make sure the boxes are up-to-date
vagrant box update

# Export the SYSTEM_COVERAGE environment variable if coverage was requested
if [[ $COVERAGE -eq 1 ]]
then
    export SYSTEM_COVERAGE="1"
fi

# Try three times to bring up the frontend
for ATTEMPT in 1 2 3
do
    if vagrant up frontend
    then
        break
    fi

    vagrant destroy -f

    if [[ $ATTEMPT -eq 3 ]]
    then
        echo "Error: failed to setup frontend"
        exit 1
    fi
done

# Run the set-up.d scripts
for SETUP_FILE in set-up.d/*
do
    if [[ -f $SETUP_FILE && -x $SETUP_FILE && $(basename $SETUP_FILE) != _* ]]
    then
        ./$SETUP_FILE $STACKI_ISO "${EXTRA_ISOS[@]}"
    fi
done
