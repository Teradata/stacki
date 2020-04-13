#! /bin/bash

PALLET_DIR=/export/stack/pallets/SLES/15sp1/sles15/sles/x86_64/
if [[ -d $PALLET_DIR ]]; then
  cp -r /opt/stack/pallet-patches/SLES-15sp1-sles15-sles-x86_64/add-stacki-squashfs/* $PALLET_DIR
fi
