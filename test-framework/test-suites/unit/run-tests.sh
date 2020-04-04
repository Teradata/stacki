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
    STACKI_ISO=$(cat .cache/state.json | python3 -c 'import sys, json; print(json.load(sys.stdin)["STACKI_ISO"])')
    if [[ $(basename $STACKI_ISO) =~ sles12\.x86_64\.disk1\.iso ]]
    then
        COVERAGERC="sles.coveragerc"
    else
        COVERAGERC="redhat.coveragerc"
    fi

    # Capture the test status but continue after failure
    set +e
    vagrant ssh frontend --no-tty -c "sudo -i /opt/stack/bin/pytest -vvv \
        --junitxml=/export/reports/unit-junit.xml \
        --cov-config=/export/test-suites/_common/$COVERAGERC \
        --cov=wsclient \
        --cov=stack \
        --cov-report html:/export/reports/unit \
        /export/test-suites/unit/tests/"
    STATUS=$?

    # Move the coverage data
    vagrant ssh frontend --no-tty -c "sudo -i mv /root/.coverage /export/reports/unit.coverage"

    exit $STATUS
else
    vagrant ssh frontend --no-tty -c "sudo -i /opt/stack/bin/pytest -vvv \
        --junitxml=/export/reports/unit-junit.xml \
        /export/test-suites/unit/tests/"
fi
