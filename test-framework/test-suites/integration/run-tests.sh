#!/bin/bash

# Bail on script errors
set -e

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

# Run the tests
if [[ $1 == "--no-cov" ]]
then
    vagrant ssh frontend -c "sudo -i pytest -vvv /export/tests/"
else
    # Figure out which .coveragerc to pass
    STACKI_ISO=$(cat .cache/state.json | python -c 'import sys, json; print json.load(sys.stdin)["STACKI_ISO"]')
    if [[ $(basename $STACKI_ISO) =~ sles12\.x86_64\.disk1\.iso ]]
    then
        COVERAGERC="sles.coveragerc"
    else
        COVERAGERC="redhat.coveragerc"
    fi

    vagrant ssh frontend -c "sudo -i pytest -vvv \
        --cov-config=/export/tests/$COVERAGERC \
        --cov=wsclient \
        --cov=stack \
        --cov-report html:/export/reports/integration \
        /export/tests/"
fi
