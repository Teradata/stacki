#!/bin/bash

# Echo out the commands to the console
set -x

# Bail on script errors
set -e

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

# Make sure we have the virtualenv activated
if [[ -z $VIRTUAL_ENV ]]
then
    source ../../bin/activate
fi

# Run the tests
vagrant ssh frontend --no-tty -c "sudo -i /opt/stack/bin/pytest -vvv \
	--junit-xml=/export/reports/system-junit.xml \
	/opt/stack/lib/python3*/site-packages/stack/commands/report/system/tests/ \
	/export/test-suites/system/tests/"

if [[ $1 == "--coverage" ]]
then
    # Generate the coverage reports
    vagrant ssh frontend --no-tty -c "sudo -i coverage combine"
    vagrant ssh frontend --no-tty -c "sudo -i coverage html -i -d /export/reports/system"

    # Move the coverage data
    vagrant ssh frontend --no-tty -c "sudo -i mv /root/.coverage /export/reports/system.coverage"
fi
