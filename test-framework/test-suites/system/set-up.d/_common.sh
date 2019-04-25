#!/bin/bash

# Bail on script errors
set -e

# Bring up the backends a bit apart
# Note: Vagrant Virtualbox provider doesn't support --parallel, so we do it here
vagrant up backend-0-0 &
sleep 10
vagrant up backend-0-1 &
sleep 10

# Monitor the backend installs
vagrant ssh frontend -c "sudo -i /export/test-suites/system/files/monitor-backends.py --timeout=$1"
