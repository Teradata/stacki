#!/bin/bash

# Bail on script errors
set -e

# Output the commands as they are run
set -x

# Copy everything to a source directory, so we aren't building on a shared folder
mkdir -p /export/src
cp -rd /vagrant /export/src/stacki
cd /export/src/stacki

# Regenerate the poetry.lock, if requested
if [[ $UPDATE_LOCKFILE == "true" ]]
then
    rm -f common/src/foundation/python-packages/poetry.lock
fi

# Figure out our ROLLVERSION
ROLLVERSION=$(make -f rollversion.mk ROLLVERSION)
if [[ $IS_RELEASE != "true" ]]
then
    ROLLVERSION=${ROLLVERSION}_$(date +%Y%m%d)_$(git rev-parse --short HEAD | cut -c -7)
fi

# Bootstrap the bootstrap. Turn of error detection because the make file
# triggers an error to stop itself.
set +e
make ROLLVERSION=$ROLLVERSION bootstrap
set -e

# Point pip at the Stacki Builds PyPI cache, if requested
if [[ $PYPI_CACHE == "true" ]]
then
    cat > "/etc/pip.conf" <<EOF
[global]
index-url = http://stacki-builds.labs.teradata.com/pypi
trusted-host = stacki-builds.labs.teradata.com
disable-pip-version-check = true
EOF
fi

# Bootstrap the build environment
source /etc/profile.d/stack-build.sh
make ROLLVERSION=$ROLLVERSION bootstrap

# Build the non-bootable stacki ISO and check that it built correctly
make ROLLVERSION=$ROLLVERSION
make ROLLVERSION=$ROLLVERSION manifest-check

# Copy the updated poetry.lock back out of the VM
if [[ $UPDATE_LOCKFILE == "true" ]]
then
    cp common/src/foundation/python-packages/poetry.lock  /vagrant/common/src/foundation/python-packages/poetry.lock
fi

# If we are redhat7 PLATFORM, we aren't done yet
if [[ $PLATFORM = "redhat7" ]]
then
    # Install stacki-fab RPMs so we can run frontend-install
    rpm -ivh "$(find . -wholename "./build-stacki-*/RPMS/x86_64/stacki-fab*.rpm")"
    # Barnacle with the non-bootable ISO
    /opt/stack/bin/frontend-install.py --use-existing --stacki-iso=$(ls -1 ./build-*/stacki-*.iso)

    # Restart httpd, it seems to be in a crashed state after barnacle
    systemctl restart httpd

    # Add the CentOS pallet
    source /etc/profile.d/stack-binaries.sh
    stack add pallet /export/isos/CentOS-7-x86_64-Everything-1810.iso
    stack enable pallet CentOS box=frontend

    # Clean the build environment
    cd /export/src/stacki/redhat/src/
    make ROLLVERSION=$ROLLVERSION nuke
    cd ../../
    make ROLLVERSION=$ROLLVERSION nuke

    # Rebuild the stacki ISO as bootable
    make ROLLVERSION=$ROLLVERSION
    make ROLLVERSION=$ROLLVERSION manifest-check
fi

# Copy the ISO out of the VM
cp build-*/stacki-*.iso /vagrant/

# Note: For now, we no longer build StackiOS
# If we have an OS_PALLET, build a stackios ISO
# if [[ $PLATFORM = "redhat7" && -n $OS_PALLET ]]
# then
#     cd /export/src
#     stack create pallet stacki/build-*/stacki-*.iso /export/isos/$(basename $OS_PALLET) name=stackios
#     cp stackios-*.iso /vagrant/
# fi

# Belt and suspenders
sync
exit 0
