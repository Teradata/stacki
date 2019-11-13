#!/bin/bash

# Call with the hooks to run. EX: run_hook "pre-frontend"
run_hooks() {
    if [[ -d "hooks/$1" ]]
    then
        for HOOK_FILE in hooks/$1/*
	    do
            if [[ -f "$HOOK_FILE" && -x "$HOOK_FILE" ]]
		    then
			    "./$HOOK_FILE"
		    fi
    	done
    fi
}

# Bail on script errors
set -e

# Parse the command line
BACKENDS=0
NAME="cluster-up-`printf '%04x%04x' $RANDOM $RANDOM`"
DOWNLOAD_DIR="."
SRC_DIR=""
EXPORT_FRONTEND=0
ISO=""
PROVIDER="virtualbox"
FQDN="frontend-0-0.localdomain"
BRIDGE=""
IP=""
NETMASK="255.255.255.0"
GATEWAY=""
DNS=""
FORWARD_PORTS=""

while [[ "$#" -gt 0 ]]
do
    case "$1" in
        --backends=*)
            BACKENDS="${1#*=}"
            shift 1
            ;;
        --name=*)
            NAME="${1#*=}"
            shift 1
            ;;
        --download-dir=*)
            DOWNLOAD_DIR="${1#*=}"
            shift 1
            ;;
        --use-the-src-dir=*)
            SRC_DIR="${1#*=}"
            shift 1
            ;;
        --export-frontend)
            EXPORT_FRONTEND=1
            shift 1
            ;;
        --fqdn=*)
            FQDN="${1#*=}"
            shift 1
            ;;
        --bridge=*)
            BRIDGE="${1#*=}"
            shift 1
            ;;
        --ip=*)
            IP="${1#*=}"
            shift 1
            ;;
        --netmask=*)
            NETMASK="${1#*=}"
            shift 1
            ;;
        --gateway=*)
            GATEWAY="${1#*=}"
            shift 1
            ;;
        --dns=*)
            DNS="${1#*=}"
            shift 1
            ;;
        --forward-ports=*)
            FORWARD_PORTS="${1#*=}"
            shift 1
            ;;
        --*)
            echo -e "\033[31mError: unrecognized flag \"$1\"\033[0m"
            exit 1
            ;;
        *)
            ISO="$1"
            shift 1
            ;;
    esac
done

if [[ -z "$ISO" ]]
then
    echo "Usage: ./cluster-up.sh [options...] STACKI_ISO"
    echo "Options:"
    echo -e "  --backends=[0-253]\t\tThe number backends to create. Default: 0"
    echo -e "  --fqdn=FQDN\t\t\tThe FQDN of the frontend. Default: cluster-up-frontend.localdomain"
    echo -e "  --name=NAME\t\t\tThe name to uniquely identify this cluster. Default: YYYYMMDD_HHMMSS_RRRR"
    echo -e "  --download-dir=DIRECTORY\tThe directory to store installer ISOs. Default: '.'"
    echo -e "  --use-the-src-dir=DIRECTORY\tThe directory will be mounted and symlinked into the frontend."
    echo -e "  --export-frontend\t\tExport the frontend as a vagrant box."
    echo -e "  --forward-ports=SRC:DST[,...]\tComma separated list of ports to forward."
    echo -e "  --bridge=INTERFACE\t\tBridge interface on the host. Default: Use host only networking"
    echo -e "  --ip=IP_ADDRESS\t\tIP Address for the bridge network. Default: Use DHCP"
    echo -e "  --netmask=NETMASK\t\tThe netmask for the bridge network. Default: 255.255.255.0"
    echo -e "  --gateway=GATEWAY_ADDRESS\tGateway address for the bridged interface."
    echo -e "  --dns=DNS_ADDRESS[,DNS2]\tComma separated list of DNS servers."
    exit 1
fi

# If we set an BRIDGE interface or IP, we disable creating virtual backends
if [[ -n "$BRIDGE" || -n $IP ]]
then
    BACKENDS=0
fi

# Make sure a sane number of backends were requested
if [[ $BACKENDS -gt 253 || $BACKENDS -lt 0 ]]
then
    echo -e "\033[31mError: backends needs to be a number between 0 and 253\033[0m"
    exit 1
fi


# Convert DOWNLOAD_DIR to be absolute
DOWNLOAD_DIR="$(cd "${DOWNLOAD_DIR/#~/$HOME}"; pwd)"
if [[ ! -z "$SRC_DIR" ]]
then
    SRC_DIR="$(cd "${SRC_DIR/#~/$HOME}"; pwd)"
fi

# Convert ISO to be absolute, if it isn't a URL
if [[ ! $ISO =~ https?:// ]]
then
    ISO="$(cd "$(dirname "${ISO/#~/$HOME}")"; pwd)/$(basename "$ISO")"
fi

# Make sure we are in the project directory
cd "$(dirname "${BASH_SOURCE[0]}")"

# Run the pre-cluster-up hooks
run_hooks "pre-cluster-up"

# Make sure we already don't have a cluster
if [[ -f .vagrant/cluster-up.json ]]
then
    echo -e "\033[31mError: a cluster already exists. Run './cluster-down.sh' to destroy it.\033[0m"
    exit 1
fi

# Figure out if we are rockin' VirtualBox or we try libvirt
if [[ ! -x "`command -v VBoxManage`" ]]
then
    # No VBoxManager, assume we are libvirt. See if we have libvirtd installed.
    if [[ ! -x "`command -v libvirtd`" ]]
    then
        echo -e "\033[31mError: It looks like you don't have VirtualBox or libvirt installed\033[0m"
        exit 1
    fi

    # See if we have the vagrant-libvirt plugin installed
    if [[ ! "`vagrant plugin list`" =~ "vagrant-libvirt" ]]
    then
        echo -e "\033[31mError: Looks like you need to install the vagrant-libvirt plugin\033[0m"
        exit 1
    else
        PROVIDER="libvirt"
    fi
fi

# If the ISO starts with http we assume it is remote and go fetch it
if [[ $ISO =~ https?:// ]]
then
    DOWNLOAD_ISO=$DOWNLOAD_DIR/`basename $ISO`

    if [[ ! -f "$DOWNLOAD_ISO" ]]
    then
        echo
        echo -e "\033[34mDownloading `basename $ISO` ...\033[0m"
        curl -f --progress-bar -o $DOWNLOAD_ISO $ISO
    fi

    ISO=$DOWNLOAD_ISO
fi

# Figure out if we are SLES or CentOS
if [[ $ISO =~  "-sles12." ]]
then
    OS="sles12"
elif [[ $ISO =~ "-redhat7." ]]
then
    OS="redhat7"
else
    echo -e "\033[31mError: Need a sles12 OR redhat7 Stacki ISO\033[0m"
    exit 1
fi

# Split up the ISO path and ISO filename
ISO_PATH=`dirname "$ISO"`
ISO_FILENAME=`basename "$ISO"`

# Write out some settings for the Vagrantfile
mkdir -p ".vagrant"
cat > ".vagrant/cluster-up.json" <<-EOF
{
    "OS": "$OS",
    "ISO_PATH": "$ISO_PATH",
    "ISO_FILENAME": "$ISO_FILENAME",
    "NAME": "$NAME",
    "BACKENDS": $BACKENDS,
    "DOWNLOAD_DIR": "$DOWNLOAD_DIR",
    "SRC_DIR": "$SRC_DIR",
    "PROVIDER": "$PROVIDER",
    "FQDN": "$FQDN",
    "BRIDGE": "$BRIDGE",
    "IP": "$IP",
    "NETMASK": "$NETMASK",
    "GATEWAY": "$GATEWAY",
    "DNS": "$DNS",
    "FORWARD_PORTS": "$FORWARD_PORTS"
}
EOF

# Download the installer ISO if it doesn't exist
if [[ $OS == "sles12" ]]
then
    if [[ ! -f "$DOWNLOAD_DIR/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso" ]]
    then
        echo
        echo -e "\033[34mDownloading SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso ...\033[0m"
        curl -f --progress-bar  --retry 3 -o $DOWNLOAD_DIR/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso http://stacki-builds.labs.teradata.com/installer-isos/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso
    fi
elif [[ $OS == "redhat7" ]]
then
    if [[ ! -f "$DOWNLOAD_DIR/CentOS-7-x86_64-Everything-1810.iso" ]]
    then
        echo
        echo -e "\033[34mDownloading CentOS-7-x86_64-Everything-1810.iso ...\033[0m"

        # Try to pull it from TD first
        set +e
        echo
        echo -e "\033[37mTrying internal Teradata first ...\033[0m"
        curl -f --progress-bar --retry 3 -o $DOWNLOAD_DIR/CentOS-7-x86_64-Everything-1810.iso http://stacki-builds.labs.teradata.com/installer-isos/CentOS-7-x86_64-Everything-1810.iso
        set -e

        if [[ ! -f $DOWNLOAD_DIR/CentOS-7-x86_64-Everything-1810.iso ]]
        then
            echo
            echo -e "\033[37mDownloading from the Internet ...\033[0m"
            curl -f --progress-bar --retry 3 -o $DOWNLOAD_DIR/CentOS-7-x86_64-Everything-1810.iso http://mirrors.edge.kernel.org/centos/7.6.1810/isos/x86_64/CentOS-7-x86_64-Everything-1810.iso
        fi
    fi
fi

# Pull frontend-install.py from the local machine if we are running from a full repo checkout
if [[ -f ../fab/frontend-install.py ]]
then
    cp ../fab/frontend-install.py .
fi

# Make sure the boxes are up-to-date
echo
echo -e "\033[34mChecking the vagrant boxes for updates ...\033[0m"
vagrant box update

# Run the pre-frontend hooks
run_hooks "pre-frontend"

# Bring up the frontend VM
echo
echo -e "\033[34mBringing up the frontend ...\033[0m"
vagrant up frontend

# Reboot the frontend after the barnacle
vagrant reload frontend

# Run the post-frontend hooks
run_hooks "post-frontend"

# Add the OS pallet
echo
echo -e "\033[34mAdding the OS pallet to the frontend ...\033[0m"
if [[ $OS == "sles12" ]]
then
    vagrant ssh frontend -c "sudo -i stack add pallet /export/installer-iso/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso"
    vagrant ssh frontend -c "sudo -i stack enable pallet SLES"
    vagrant ssh frontend -c "sudo -i stack enable pallet SLES box=frontend"
elif [[ $OS == "redhat7" ]]
then
    vagrant ssh frontend -c "sudo -i stack add pallet /export/installer-iso/CentOS-7-x86_64-Everything-1810.iso"
    vagrant ssh frontend -c "sudo -i stack enable pallet CentOS"
    vagrant ssh frontend -c "sudo -i stack enable pallet CentOS box=frontend"
fi

# Copy the vagrant cart into place and enable it
echo
echo -e "\033[34mAdding the vagrant cart to the frontend ...\033[0m"
vagrant ssh frontend -c "sudo -i cp -r /vagrant/cart /export/stack/carts/vagrant"
vagrant ssh frontend -c "sudo -i stack add cart vagrant"
vagrant ssh frontend -c "sudo -i stack enable cart vagrant"

# Export the frontend box, if requested
if [[ $EXPORT_FRONTEND -eq 1 ]]
then
    # Run the pre-export hooks
    run_hooks "pre-export"

    # Package up the frontend
    BOX_NAME=$ISO_PATH/${ISO_FILENAME/.iso/.box}
    BOX_JSON=$ISO_PATH/${ISO_FILENAME/.iso/.json}
    BOX_VERSION=$(vagrant ssh frontend -c "sudo -i stack report version" | tr -d '\r' | tr '_' '-')

    set +e
    SHASUM_EXE=$(which sha1sum)
    [ -z $SHASUM_EXE ] && SHASUM_EXE=$(which shasum)
    set -e

    echo
    echo -e "\033[34mExporting the frontend as a vagrant box ...\033[0m"
    vagrant halt frontend
    vagrant package --output $BOX_NAME frontend
    BOX_SHA=$($SHASUM_EXE $BOX_NAME | awk '{print $1;}')
    cat > $BOX_JSON <<EOF
{
    "name": "stacki/frontend/$OS",
    "versions": [{
        "version": "${BOX_VERSION}",
        "providers": [
            {
                "name": "${PROVIDER}",
                "url": "${BOX_NAME}",
                "checksum_type": "sha1",
                "checksum": "${BOX_SHA}"
            }
        ]
    }]
}
EOF

    vagrant up frontend

    # Run the post-export hooks
    run_hooks "post-export"
fi

if [[ $BACKENDS -gt 0 ]]
then
    echo
    echo -e "\033[34mBringing up the $BACKENDS backend(s) ...\033[0m"

    # Start up node discovery
    vagrant ssh frontend -c "sudo -i stack enable discovery"

    # Run the pre-backends hooks
    run_hooks "pre-backends"

    # Bring up the backends
    set +e
    for ((i=0; i < $BACKENDS; i += 1))
    do
        # The libvirt vagrant provider doesn't support boot_timeout, so we ignore
        # errors and check for ssh to come up later on.
        vagrant up --no-destroy-on-error backend-0-$i &
        sleep 10
    done

    # Wait for them to finish installing themselves, or in the case of libvirt,
    # to timeout before install is done.
    wait

    # Check that the backends are really up
    for ((i=0; i < $BACKENDS; i += 1))
    do
        BACKEND_UP[$i]=0
    done
    BACKENDS_UP=0

    # Check for the backends to come up for roughly an hour
    for ((attempt=0; attempt < 60; attempt += 1))
    do
        for ((i=0; i < $BACKENDS; i += 1))
        do
            if [[ BACKEND_UP[$i] -eq 0 ]]
            then
                vagrant ssh backend-0-$i -c "echo backend-0-$i is up" 2>/dev/null
                if [[ $? -eq 0 ]]
                then
                    BACKEND_UP[$i]=1
                    BACKENDS_UP=$((BACKENDS_UP + 1))
                fi
            fi
        done

        if [[ $BACKENDS_UP -eq $BACKENDS ]]
        then
            break
        else
            sleep 55
        fi
    done
    set -e

    # Run the post-backends hooks
    run_hooks "post-backends"

    # Shut down node discovery
    vagrant ssh frontend -c "sudo -i stack disable discovery"
fi

# Write out the access instructions
set +x
echo
echo
echo "    ###############################"
echo
echo "                SUCCESS"
echo
echo "       To log in to the frontend:"
echo
echo "       vagrant ssh frontend"

if [[ $BACKENDS -gt 0 ]]
then
    echo
    echo
    echo "       To log in to the backend(s):"
    echo
    for ((i=0; i < $BACKENDS; i += 1))
    do
        echo "       vagrant ssh backend-0-$i"
    done
fi

echo
echo "    ###############################"
echo
echo

# if we mapped the stacki source, symlink it in to place
if [[ -d "$SRC_DIR" ]]
then
    vagrant ssh frontend -c "sudo -i python3 /export/src/tools/use_the_source/use_the_source.py /export/src/"
fi

# Run the post-cluster-up hooks
run_hooks "post-cluster-up"

# Have vagrant ssh automatically sudo to root
vagrant ssh frontend -c 'echo "if [[ -n \$SSH_TTY ]] && [[ \$- =~ i ]]; then exec sudo -i; fi" >> /home/vagrant/.bash_profile'

exit 0
