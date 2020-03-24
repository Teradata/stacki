#!/bin/bash

# Bail on script errors
set -e

# Output the commands as they are run
set -x

# Set up the platform repos and install git
cd /export/isos/
INSTALLER_ISOS=http://stacki-builds.labs.teradata.com/installer-isos

if [[ $PLATFORM = "sles11" ]]
then
    if [[ ! -f SLES-11-SP3-DVD-x86_64-GM-DVD1.iso ]]
    then
        curl -sfSLO --retry 3 $INSTALLER_ISOS/SLES-11-SP3-DVD-x86_64-GM-DVD1.iso
    fi

    if [[ $(md5sum SLES-11-SP3-DVD-x86_64-GM-DVD1.iso | cut -c 1-32) != "480b70d50cbb538382dc2b9325221e1b" ]]
    then
        echo "Error: SLES-11-SP3-DVD-x86_64-GM-DVD1.iso is corrupt"
        exit 1
    fi

    if [[ ! -f SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso ]]
    then
        curl -sfSLO --retry 3 $INSTALLER_ISOS/SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso
    fi

    if [[ $(md5sum SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso | cut -c 1-32) != "61d0d77b9d48ad3786fcbba984d77f42" ]]
    then
        echo "Error: SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso is corrupt"
        exit 1
    fi

    zypper addrepo iso:/?iso=/export/isos/SLES-11-SP3-DVD-x86_64-GM-DVD1.iso os
    zypper addrepo iso:/?iso=/export/isos/SLE-11-SP3-SDK-DVD-x86_64-GM-DVD1.iso sdk

    zypper install -y git-core

elif [[ $PLATFORM = "sles12" ]]
then
    if [[ ! -f SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso ]]
    then
        curl -sfSLO --retry 3 $INSTALLER_ISOS/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso
    fi

    if [[ $(md5sum SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso | cut -c 1-32) != "633537da81d270a9548272dfe1fdd20d" ]]
    then
        echo "Error: SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso is corrupt"
        exit 1
    fi

    if [[ ! -f SLE-12-SP3-SDK-DVD-x86_64-GM-DVD1.iso ]]
    then
        curl -sfSLO --retry 3 $INSTALLER_ISOS/SLE-12-SP3-SDK-DVD-x86_64-GM-DVD1.iso
    fi

    if [[ $(md5sum SLE-12-SP3-SDK-DVD-x86_64-GM-DVD1.iso | cut -c 1-32) != "63d5a90ec214f5722acf9c78b3d55043" ]]
    then
        echo "Error: SLE-12-SP3-SDK-DVD-x86_64-GM-DVD1.iso is corrupt"
        exit 1
    fi

    zypper addrepo iso:/?iso=/export/isos/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso os
    zypper addrepo iso:/?iso=/export/isos/SLE-12-SP3-SDK-DVD-x86_64-GM-DVD1.iso sdk

    zypper install -y git-core

elif [[ $PLATFORM = "sles15" ]]
then
    if [[ ! -f SLE-15-SP1-Installer-DVD-x86_64-GM-DVD1.iso ]]
    then
        curl -sfSLO --retry 3 $INSTALLER_ISOS/SLE-15-SP1-Installer-DVD-x86_64-GM-DVD1.iso
    fi

    if [[ $(md5sum SLE-15-SP1-Installer-DVD-x86_64-GM-DVD1.iso | cut -c 1-32) != "f61a98405b233c62f5b8d48ac6c611d4" ]]
    then
        echo "Error: SLE-15-SP1-Installer-DVD-x86_64-GM-DVD1.iso is corrupt"
        exit 1
    fi

    if [[ ! -f SLE-15-SP1-Packages-x86_64-GM-DVD1.iso ]]
    then
        curl -sfSLO --retry 3 $INSTALLER_ISOS/SLE-15-SP1-Packages-x86_64-GM-DVD1.iso
    fi

    if [[ $(md5sum SLE-15-SP1-Packages-x86_64-GM-DVD1.iso | cut -c 1-32) != "1caa5d8348ac16f793d716a4b78cd948" ]]
    then
        echo "Error: SLE-15-SP1-Packages-x86_64-GM-DVD1.iso is corrupt"
        exit 1
    fi

    # Virtualbox is flaky with using large ISOs in a shared folder, so copy them into the VM
    cp SLE-15-*.iso /export/

    zypper addrepo iso:/?iso=/export/SLE-15-SP1-Installer-DVD-x86_64-GM-DVD1.iso os
    zypper addrepo iso:/?iso=/export/SLE-15-SP1-Packages-x86_64-GM-DVD1.iso packages

    zypper install -y git-core

else
    if [[ ! -f CentOS-7-x86_64-Everything-1810.iso ]]
    then
        if [[ $INTERNAL == "true" ]]
        then
            curl -sfSLO --retry 3 $INSTALLER_ISOS/CentOS-7-x86_64-Everything-1810.iso
        else
            curl -sfSLO --retry 3  http://mirrors.edge.kernel.org/centos/7.6.1810/isos/x86_64/CentOS-7-x86_64-Everything-1810.iso
        fi
    fi

    if [[ $(md5sum CentOS-7-x86_64-Everything-1810.iso | cut -c 1-32) != "41e58360e224b49e96e44b94e1563c1f" ]]
    then
        echo "Error: CentOS-7-x86_64-Everything-1810.iso is corrupt"
        exit 1
    fi

    mkdir -p /media/cdrom
    mount -o loop /export/isos/CentOS-7-x86_64-Everything-1810.iso /media/cdrom
    rm /etc/yum.repos.d/*.repo
    cat > "/etc/yum.repos.d/dvd.repo" <<EOF
[dvd]
name=CentOS-7-x86_64-Everything-1810.iso
baseurl=file:///media/cdrom/
gpgcheck=0
enabled=1
assumeyes=1
EOF

    yum update
    yum -y install git
fi
