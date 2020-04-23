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
  rpm -Uv $images
fi

# Copy the vmlinuz and initrd
cp /opt/stack/images/initrd-sles-sles11-11sp3-x86_64 /tftpboot/pxelinux/
cp /opt/stack/images/initrd-sles-sles12-12sp2-x86_64 /tftpboot/pxelinux/
cp /opt/stack/images/initrd-sles-sles12-12sp3-x86_64 /tftpboot/pxelinux/

cp /opt/stack/images/vmlinuz-sles-sles11-11sp3-x86_64 /tftpboot/pxelinux/
cp /opt/stack/images/vmlinuz-sles-sles12-12sp2-x86_64 /tftpboot/pxelinux/
cp /opt/stack/images/vmlinuz-sles-sles12-12sp3-x86_64 /tftpboot/pxelinux/

# Now try to run the pallet patches, but allow these to fail.
set +e

../SLES-12sp2-sles12-sles-x86_64/010-add-stacki-squashfs.sh
../SLES-12sp3-sles12-sles-x86_64/010-add-stacki-squashfs.sh
../SLES-11sp3-sles11-sles-x86_64/010-add-stacki-squashfs.sh
