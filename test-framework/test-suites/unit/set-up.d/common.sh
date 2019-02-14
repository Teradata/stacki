#!/bin/bash

# Bail on script errors
set -e

# Install pytest-cov on the frontend
vagrant ssh frontend -c "sudo -i python3 -m ensurepip"
vagrant ssh frontend -c "sudo -i pip3 install pytest-cov"
