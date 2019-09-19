#!/bin/bash

# Bail on script errors
set -e

# Add hosts which are going to get specific partitioning setups for testing
stack load hostfile file=/export/test-suites/system/files/hosts.csv

# Load partitioning information for backend-0-0 and backend-0-1
stack load storage partition file=/export/test-suites/system/files/lvm-complex.csv
stack load storage partition file=/export/test-suites/system/files/quoted-options.csv

# Set the installer to use the graphical installer
stack set host bootaction a:backend type=install action="default"

# Set our backends to install next boot
stack set host boot a:backend action=install nukedisks=true nukecontroller=true
