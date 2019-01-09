#!/bin/bash

# Bail on script errors
set -e

# Make sure we are in the same directory as this script
cd "$(dirname "${BASH_SOURCE[0]}")"

# Destroy the vagrant machines
vagrant destroy -f

# Remove the .cache folder
rm -rf .cache
