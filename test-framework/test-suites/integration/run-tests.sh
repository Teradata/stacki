#!/bin/bash

# Echo out the commands to the console
set -x

# Bail on script errors
set -e

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

# Run the tests
if [[ $1 == "--coverage" ]]
then
    # Figure out which .coveragerc to pass
    STACKI_ISO=$(cat .cache/state.json | python -c 'import sys, json; print json.load(sys.stdin)["STACKI_ISO"]')
    if [[ $(basename $STACKI_ISO) =~ sles12\.x86_64\.disk1\.iso ]]
    then
        COVERAGERC="sles.coveragerc"
    else
        COVERAGERC="redhat.coveragerc"
    fi

    # Capture the test status but continue after failure
    set +e
    vagrant ssh frontend -c "sudo -i pytest -vvv \
        --dist=loadfile -n 4 \
        --reruns=1 --reruns-delay=10 \
        --timeout=300 --timeout_method=signal \
        --junit-xml=/export/reports/integration-junit.xml \
        --cov-config=/export/test-suites/_common/$COVERAGERC \
        --cov=wsclient \
        --cov=stack \
        --cov-report html:/export/reports/integration \
        /export/test-suites/integration/tests/"
    STATUS=$?

    # Move the coverage data
    vagrant ssh frontend -c "sudo -i mv /root/.coverage /export/reports/integration.coverage"

    exit $STATUS
elif [[ $1 == "--audit" ]]
then
    vagrant ssh frontend -c "sudo -i pytest -vvv \
        --audit -n 1 \
        /export/test-suites/integration/tests/"
else
    vagrant ssh frontend -c "sudo -i pytest -vvv \
        --dist=loadfile -n 4 \
        --reruns=1 --reruns-delay=10 \
        --timeout=300 --timeout_method=signal \
        --junit-xml=/export/reports/integration-junit.xml \
        /export/test-suites/integration/tests/"
fi
