#!/bin/bash

# Bail on script errors
set -e

# Parse the command line
ALL=1
UNIT=0
INTEGRATION=0
SYSTEM=0
COVERAGE=0

ISO=""
TEMP_EXTRA_ISOS=()
EXTRA_ISOS=()

while [[ "$#" -gt 0 ]]
do
    case "$1" in
        --unit)
            UNIT=1
            ALL=0
            shift 1
            ;;
        --integration)
            INTEGRATION=1
            ALL=0
            shift 1
            ;;
        --system)
            SYSTEM=1
            ALL=0
            shift 1
            ;;
        --coverage)
            COVERAGE=1
            shift 1
            ;;
        --extra-isos=*)
            TEMP_EXTRA_ISOS=($(echo "${1#*=}" | tr ',' '\n'))
            shift 1
            ;;
        *)
            ISO="$1"
            shift 1
            ;;
    esac
done

# Create the .cache directory and get a full path to it
CACHE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)/.cache"
if [[ ! -d "$CACHE_DIR" ]]
then
    mkdir "$CACHE_DIR"
fi

# If extra ISOs were passed in, have to do some post-processing
if [[ ${#TEMP_EXTRA_ISOS[@]} -gt 0 ]]
then
    # Check that the extra isos exist, copy them to .cache, and
    # get the full paths to them
    for EXTRA_ISO in "${TEMP_EXTRA_ISOS[@]}"
    do
        # Make sure that the EXTRA_ISO actually exists
        if [[ ! -f "$EXTRA_ISO" ]]
        then
            echo
            echo -e "\033[31mError: $EXTRA_ISO doesn't exist\033[0m"
            echo
            exit 1
        fi

        # Copy the EXTRA_ISO to the .cache directory
        cp "$EXTRA_ISO" "$CACHE_DIR" 2>/dev/null

        # Add the full path to the EXTRA_ISOS array
        EXTRA_ISOS+=("$CACHE_DIR/$(basename "$EXTRA_ISO")")
    done
fi

# Make sure we are passed an ISO to test
if [[ -z "$ISO" ]]
then
    echo "Usage: ./run-tests.sh [flags...] STACKI_ISO"
    echo
    echo "Flags to run individual test suite types:"
    echo "  --unit"
    echo "  --integration"
    echo "  --system"
    echo
    echo "Extra ISOs can be passed to the system test suite:"
    echo "  --extra-isos=ISO1,ISO2"
    echo
    echo "To enable code coverage report generation, use the flag:"
    echo "  --coverage"
    exit 1
fi

# See if we need to download the ISO
if [[ $ISO =~ https?:// ]]
then
    # Make sure we are in the project directory
    cd "$(dirname "${BASH_SOURCE[0]}")"

    # Download the ISO if needed
    cd .cache
    if [[ ! -f "$(basename "$ISO")" ]]
    then
        echo
        echo -e "\033[34mDownloading $(basename "$ISO") ...\033[0m"
        curl -f --progress-bar -O "$ISO"
    fi

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
    ISO="$(cd "$(dirname "$ISO")"; pwd)/$(basename "$ISO")"

    # Make sure we are in the project directory
    cd "$(dirname "${BASH_SOURCE[0]}")"

    # Copy the ISO to the cache directory
    cp "$ISO" .cache/ 2>/dev/null
fi

# Make sure the reports directory exists
if [[ ! -d "reports" ]]
then
    mkdir "reports"
fi

# Activate the Python venv
if [[ ! -f "bin/activate" ]]
then
    echo
    echo -e "\033[31mError: you must run 'make' first to build the test environment\033[0m"
    echo
    exit 1
fi

source bin/activate

# Get the full path of our ISO file in the .cache directory
STACKI_ISO="$(pwd)/.cache/$(basename "$ISO")"

# Allow things to progress on error at this point
set +e

# Run the unit test suite, if requested
if [[ $ALL -eq 1 || $UNIT -eq 1 ]]
then
    echo
    echo -e "\033[34mRunning unit test suite ...\033[0m"
    ./test-suites/unit/set-up.sh $STACKI_ISO

    if [[ $COVERAGE -eq 1 ]]
    then
        ./test-suites/unit/run-tests.sh --coverage
    else
        ./test-suites/unit/run-tests.sh
    fi
    RETURN_CODE=$?

    ./test-suites/unit/tear-down.sh

    if [[ $RETURN_CODE -ne 0 ]]
    then
        echo
        echo -e "\033[31mError: one or more unit tests failed\033[0m"
        echo
        exit 1
    fi
fi

# Run the integration test suite, if requested
if [[ $ALL -eq 1 || $INTEGRATION -eq 1 ]]
then
    echo
    echo -e "\033[34mRunning integration test suite ...\033[0m"
    ./test-suites/integration/set-up.sh $STACKI_ISO

    if [[ $COVERAGE -eq 1 ]]
    then
        ./test-suites/integration/run-tests.sh --coverage
    else
        ./test-suites/integration/run-tests.sh
    fi
    RETURN_CODE=$?

    ./test-suites/integration/tear-down.sh

    if [[ $RETURN_CODE -ne 0 ]]
    then
        echo
        echo -e "\033[31mError: one or more integration tests failed\033[0m"
        echo
        exit 1
    fi
fi

# Run the system test suite, if requested
if [[ $ALL -eq 1 || $SYSTEM -eq 1 ]]
then
    echo
    echo -e "\033[34mRunning system test suite ...\033[0m"
    ./test-suites/system/set-up.sh $STACKI_ISO "${EXTRA_ISOS[@]}"

    ./test-suites/system/run-tests.sh
    RETURN_CODE=$?

    ./test-suites/system/tear-down.sh

    if [[ $RETURN_CODE -ne 0 ]]
    then
        echo
        echo -e "\033[31mError: one or more system tests failed\033[0m"
        echo
        exit 1
    fi
fi

# Deactive the Python venv
deactivate
