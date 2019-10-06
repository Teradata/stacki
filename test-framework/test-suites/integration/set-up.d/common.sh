#!/bin/bash

# Bail on script errors
set -e

# Install pytest-cov on the frontend
vagrant ssh frontend -c "sudo -i python3 -m ensurepip"
vagrant ssh frontend -c "sudo -i pip3 install pytest-cov==2.6.1 pytest-xdist==1.27.0 pytest-rerunfailures==7.0 pytest-timeout==1.3.3"