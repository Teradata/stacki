#!/bin/bash

# Bring up the backends in order, so we know the IPs even though we are using discovery
vagrant up backend-0-0 &
vagrant ssh frontend --no-tty -c "sudo -i /export/test-suites/system/files/wait-for-backend.sh 192.168.0.1"

vagrant up backend-0-1 &
vagrant ssh frontend --no-tty -c "sudo -i /export/test-suites/system/files/wait-for-backend.sh 192.168.0.3"

vagrant up backend-0-2 &
vagrant ssh frontend --no-tty -c "sudo -i /export/test-suites/system/files/wait-for-backend.sh 192.168.0.4"

# Monitor the backend installs
vagrant ssh frontend --no-tty -c "sudo -i /export/test-suites/system/files/monitor-backends.py --timeout=$1"
