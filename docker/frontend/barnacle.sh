#! /bin/bash
#
# This needs to stay really small, the only goal here is to get far
# enought to generate a Frontend profile and then use that to install
# all the packages required for a Frontend. This does not run the
# script sections of the profile as that is machine dependent, that
# will be done on first boot. This code should also work on any OS and
# any version of stacki, hence lots of wildcard globbing and checking
# for the correct system level packaging tools.
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

STACK=/opt/stack/bin/stack

# Untar the stacki.tar pallet and install what we need to build a
# machine profile. The globbing is done to keep this code portable.
#
# We also need to add /opt/stack/lib to the shared libraries search
# path.

mkdir -p /export/stack/pallets
tar -xf stacki.tar -C /export/stack/pallets

pushd /export/stack/pallets
cd stacki/*/*/*/*/RPMS/
for pkg in foundation-python stack-command stack-pylib; do
	rpm -Uhv $pkg-*.rpm
done

popd

echo /opt/stack/lib > /etc/ld.so.conf.d/stacki.conf
ldconfig

# Add Stacki to the package repositories (yum only right now)

pushd /export/stack/pallets/stacki/*/*/*/*
url=`pwd`
popd

if [ -d /etc/yum.repos.d ]; then
	cat > /etc/yum.repos.d/stacki.repo <<EOF
[stacki]
name=stacki
baseurl=file://$url
assumeyes=1
gpgcheck=no
EOF
fi


# Build rolls.xml file for the stack pallet

pushd /export/stack/pallets/*
name=$(basename `pwd`)
cd *
version=$(basename `pwd`)
cd *
release=$(basename `pwd`)
cd *
os=$(basename `pwd`)
cd *
arch=$(basename `pwd`)
popd

cat > rolls.xml <<EOF
<rolls>
	<roll url="/export/stack/pallets" name="$name" version="$version" release="$release" os="$os" arch="$arch"/>
</rolls>
EOF

# generate a new siteattrs from current network config
# generate a new profile.sh
# run the packages section (skip the scripts)

$STACK report siteattr > site.attrs
echo platform:docker  >> site.attrs

$STACK list node xml server attrs=site.attrs > profile.xml
cat profile.xml | $STACK list host profile chapter=main profile=bash > profile.sh
bash profile.sh -spackages

systemctl disable firewalld # this breaks docker-compose

# finish the barnacle when container is run
systemctl enable stack-docker-barnacle



