#! /bin/bash

set -e

# Install the stacki RedHat images.
yum --assumeyes install stack-images

# Copy the vmlinuz and initrd. Redhat throws the version in the filename
# so we use * to ignore that.
cp /opt/stack/images/initrd.img*redhat7-x86_64 /tftpboot/pxelinux/
cp /opt/stack/images/vmlinuz*redhat7-x86_64 /tftpboot/pxelinux/
