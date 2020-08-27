#! /bin/bash

set -e

# Install the stack SLES images.  Use find + rpm because networking might be in a bad state.
PALLET_DIR=/export/stack/pallets/${name}/${version}/${rel}/${os}/${arch}/
images=$(find $PALLET_DIR -name stack-${os}-${rel}-images*rpm)
if (( $(echo $images | wc --lines) > 1 )); then
  echo found more than one stack-images package in ${PALLET_DIR}:
  echo $images
  exit 1
else
  echo installing $images
  rpm --force -Uv $images
fi

# Copy the vmlinuz and initrd
cp /opt/stack/images/initrd-sles-sles15-15sp1-x86_64 /tftpboot/pxelinux/
cp /opt/stack/images/vmlinuz-sles-sles15-15sp1-x86_64 /tftpboot/pxelinux/

# Now try to run the pallet patches, but allow these to fail.
set +e

../SLES-15sp1-sles15-sles-x86_64/010-add-stacki-squashfs.sh
