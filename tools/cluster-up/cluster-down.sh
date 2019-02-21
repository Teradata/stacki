#!/bin/bash

# Make sure we are in the project directory
cd `dirname "${BASH_SOURCE[0]}"`

# Make sure we actually have a cluster
if [[ ! -f .vagrant/cluster-up.json ]]
then
    echo -e "\033[31mError: no cluster exists.\033[0m"
    exit 1
fi

# Destroy the virtual machines
vagrant destroy -f

# Remove the cluster-up settings
rm -f ./.vagrant/cluster-up.json

exit 0
