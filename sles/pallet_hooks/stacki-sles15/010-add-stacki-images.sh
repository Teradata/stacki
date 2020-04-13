#! /bin/bash

set -e

# Install the stack SLES images.
zypper --non-interactive install stack-sles-sles15-images

# Copy the vmlinuz and initrd
cp /opt/stack/images/initrd-sles-sles15-15sp1-x86_64 /tftpboot/pxelinux/
cp /opt/stack/images/vmlinuz-sles-sles15-15sp1-x86_64 /tftpboot/pxelinux/

# Now try to run the pallet patches, but allow these to fail.
set +e

../SLES-15sp1-sles15-sles-x86_64/010-add-stacki-squashfs.sh
