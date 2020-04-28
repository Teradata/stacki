#! /bin/bash

set -e

# Install the stacki RedHat images.  Use find + rpm because networking might be in a bad state.
PALLET_DIR=/export/stack/pallets/${name}/${version}/${rel}/${os}/${arch}/
images=$(find $PALLET_DIR -name stack-images*rpm)
if (( $(echo $images | wc --lines) > 1 )); then
  echo found more than one stack-images package in ${PALLET_DIR}:
  echo $images
  exit 1
else
  echo installing $images
  rpm --force -Uv $images
fi

# Copy the vmlinuz and initrd. Redhat throws the version in the filename
# so we use * to ignore that.
cp /opt/stack/images/initrd.img*redhat7-x86_64 /tftpboot/pxelinux/
cp /opt/stack/images/vmlinuz*redhat7-x86_64 /tftpboot/pxelinux/
