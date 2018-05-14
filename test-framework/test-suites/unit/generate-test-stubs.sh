#!/bin/bash

# Bail on script errors
set -e

# Make sure we are passed the root to a stacki source tree
if [[ -z "$1" ]]
then
    echo "Usage: ./generate-test-stubs.sh STACKI_SOURCE_TREE_ROOT"
    exit 1
fi

# Get the full path to common/src/stack in the Stacki source tree 
ROOT="$(cd "$1"; pwd)/common/src/stack"

# Find all the Python files
FILES="$(cd $ROOT; find . -type d -name "tests" -prune -o -name '*.py' -print | cut -c 3-)"

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

# Tests are created in the "tests" folder
cd tests

# Generate the stubs
for FILE in $FILES
do  
    # Get the directory for the test
    TEST_DIR="$(dirname "$FILE")"

    # Generate the test file name by replacing / with _ in the path
    TEST_FILE="test_${FILE//\//_}"

    # Create the directory if missing
    mkdir -p "$TEST_DIR"

    # See if we need to create the test file
    if [[ ! -f "$TEST_DIR/$TEST_FILE" ]]
    then
        touch "$TEST_DIR/$TEST_FILE"

        echo "Created: $TEST_DIR/$TEST_FILE"
    fi
done
