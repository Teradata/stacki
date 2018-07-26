#!/bin/bash

# Bail on script errors
set -e

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"
single_test=""
pytest="pytest"
while [[ "$#" -gt 0 ]]
do
    case "$1" in
        --no-cov)
            NO_COV=1
            shift 1
            ;;
        --vvv)
            pytest="pytest -vvv"
            shift 1
            ;;
        *)
            # Only run specific tests
            if [ -d "./tests/$1" ] || [ -f  "./tests/$1" ]; then
                single_test="$1"
                echo "Only running tests for $1*"
                NO_COV=1
                pytest="pytest -vvv"
            fi
            shift 1
            ;;
    esac
done

# Run the tests
if [[ NO_COV ]]
then
    vagrant ssh frontend -c "sudo -i $pytest /export/tests/$single_test"
else
    vagrant ssh frontend -c "sudo -i $pytest \
        --cov=/opt/stack/lib/python3.6/site-packages/stack \
        --cov-report term \
        --cov-report html:/export/reports/integration \
        /export/tests/"
fi
