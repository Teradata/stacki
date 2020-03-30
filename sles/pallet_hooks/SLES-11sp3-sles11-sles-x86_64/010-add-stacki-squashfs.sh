#! /bin/bash

PALLET_DIR=/export/stack/pallets/SLES/11sp3/sles11/sles/x86_64/
if [[ -d $PALLET_DIR ]]; then
  cp -r /opt/stack/pallet-patches/SLES-11sp3-sles11-sles-x86_64/add-stacki-squashfs/* $PALLET_DIR
fi
