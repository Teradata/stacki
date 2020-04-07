#!/bin/bash

# Bail on script errors
set -e

# Make the sles11sp3 box on the frontend
stack add box sles11sp3

# Add the SLES11 pallet to the box
cp /export/cache/SLES-11-SP3-DVD-x86_64-GM-DVD1.iso /export/isos/
stack add pallet /export/isos/SLES-11-SP3-DVD-x86_64-GM-DVD1.iso
stack enable pallet SLES version=11sp3 box=sles11sp3

# Add the SLES11 SDK pallet to the box
cp /export/cache/SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso /export/isos/
stack add pallet /export/isos/SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso
stack enable pallet SLE-SDK version=11sp3 box=sles11sp3

# Add the SLES11 Stacki ISO to the box
cp /export/cache/$1 /export/isos/
stack add pallet /export/isos/$1
stack enable pallet stacki release=sles11 box=sles11sp3

# Add the vagrant cart to the box
stack enable cart vagrant box=sles11sp3
