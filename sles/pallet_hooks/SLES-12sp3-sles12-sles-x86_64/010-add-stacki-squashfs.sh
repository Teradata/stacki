#! /bin/bash

PALLET_DIR=/export/stack/pallets/SLES/12sp3/sles12/sles/x86_64/
if [[ -d $PALLET_DIR ]]; then
  cp -r /opt/stack/pallet-patches/SLES-12sp3-sles12-sles-x86_64/add-stacki-squashfs/* $PALLET_DIR
fi
