#! /bin/bash

# Try to run the pallet patches, but allow these to fail.
# The sles11 initrd and vmlinuz are in the sles12 stacki iso, so
# it should already be set up for us.
set +e

../SLES-11sp3-sles11-sles-x86_64/010-add-stacki-squashfs.sh
