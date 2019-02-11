#!/bin/bash

# Bail on script errors
set -e

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

# Run the tests
if [[ $1 == "--no-cov" ]]
then
    vagrant ssh frontend -c "sudo -i pytest -vvv \
        --dist=loadfile -n 4 \
        --reruns 2 --reruns-delay 5 \
        /export/tests/"

elif [[ $1 == "--audit" ]]
then
    vagrant ssh frontend -c "sudo -i pytest -vvv --audit -n 1 /export/tests/"
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
        --dist=loadfile -n 4 \
        --reruns 2 --reruns-delay 5 \
        --cov-config=/export/tests/$COVERAGERC \
        --cov=wsclient \
        --cov=stack \
        --cov-report html:/export/reports/integration \
        /export/tests/"
fi
