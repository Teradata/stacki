#!/bin/bash

# Echo out the commands to the console
set -x

# Bail on script errors
set -e

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

# Parse the command line
COVERAGE=0
AUDIT=0
EXTRA_FLAGS=()

while [[ "$#" -gt 0 ]]
do
    case "$1" in
        --coverage)
            COVERAGE=1
            shift 1
            ;;
        --audit)
            AUDIT=1
            shift 1
            ;;
        *)
            EXTRA_FLAGS+=("$1")
            shift 1
            ;;
    esac
done

# Run the tests
if [[ $COVERAGE -eq 1 ]]
then
    # Figure out which .coveragerc to pass
    STACKI_ISO=$(cat .cache/state.json | python3 -c 'import sys, json; print(json.load(sys.stdin)["STACKI_ISO"])')
    if [[ $(basename $STACKI_ISO) =~ sles1.\.x86_64\.disk1\.iso ]]
    then
        COVERAGERC="sles.coveragerc"
    else
        COVERAGERC="redhat.coveragerc"
    fi

    # Capture the test status but continue after failure
    set +e
    vagrant ssh frontend --no-tty -c "sudo -i /opt/stack/bin/pytest -vvv \
        --timeout=300 --timeout_method=signal \
        --junit-xml=/export/reports/integration-junit.xml \
        --cov-config=/export/test-suites/_common/$COVERAGERC \
        --cov=wsclient \
        --cov=stack \
        --cov-report html:/export/reports/integration \
        ${EXTRA_FLAGS[*]} \
        /export/test-suites/integration/tests/"
    STATUS=$?

    # Move the coverage data
    vagrant ssh frontend --no-tty -c "sudo -i mv /root/.coverage /export/reports/integration.coverage"

    exit $STATUS
elif [[ $AUDIT -eq 1 ]]
then
    vagrant ssh frontend --no-tty -c "sudo -i /opt/stack/bin/pytest -vvv \
        --audit \
        ${EXTRA_FLAGS[*]} \
        /export/test-suites/integration/tests/"
else
    vagrant ssh frontend --no-tty -c "sudo -i /opt/stack/bin/pytest -vvv \
        --timeout=300 --timeout_method=signal \
        --junit-xml=/export/reports/integration-junit.xml \
        ${EXTRA_FLAGS[*]} \
        /export/test-suites/integration/tests/"
fi
