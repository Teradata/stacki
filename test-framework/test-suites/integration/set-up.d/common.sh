#!/bin/bash

# Bail on script errors
set -e

# Install pytest-cov on the frontend
vagrant ssh frontend -c "sudo -i python3 -m ensurepip"
vagrant ssh frontend -c "sudo -i pip3 install pytest-cov==2.8.1 pytest-test-groups==1.0.3 pytest-timeout==1.3.3 coverage==4.5.4"
