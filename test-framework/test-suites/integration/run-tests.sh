#!/bin/bash

# Bail on script errors
set -e

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

# Run the tests
if [[ $1 == "--no-cov" ]]
then
    vagrant ssh frontend -c "sudo -i pytest /export/tests/"
else
    vagrant ssh frontend -c "sudo -i pytest \
        --cov=/opt/stack/lib/python3.6/site-packages/stack \
        --cov-report term \
        --cov-report html:/export/reports/integration \
        /export/tests/"
fi
