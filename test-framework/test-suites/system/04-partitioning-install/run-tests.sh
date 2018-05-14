#!/bin/bash

# Bail on script errors
set -e

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

if [[ ! -f ".cache/state.json" ]]; then
    exit 0
fi

# Run the tests
#pytest --hosts=frontend --ssh-config=".cache/ssh-config" tests/
# To run in parallel:
pytest -n 6 --hosts=frontend --ssh-config=".cache/ssh-config" tests/ -vvv
