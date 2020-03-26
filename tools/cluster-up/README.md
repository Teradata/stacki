# Stacki Cluster Up

This project will bring up a cluster of boxes consisting of a Stacki frontend and an optional number of backends.

## Installation

You need to have [Vagrant](https://www.vagrantup.com/) installed, and either
[VirtualBox](https://www.virtualbox.org/) or Libvirt/KVM. If using Libvirt/KVM, you also need to
[install the vagrant-libvirt plugin](https://github.com/vagrant-libvirt/vagrant-libvirt#installation)
and NFS server on the host. Then clone this project on your computer.

*Also of note:* You need to be on the Teradata network, either in the building or VPN'ed in, to use a SLES version of Stacki to bring up a cluster with this tool.

## Usage
Open up a terminal on your computer, change to the project directory, then run:

    ./cluster-up.sh [options...] STACKI_ISO

where STACKI_ISO is the path to the Stacki ISO you want to base the cluster on.
It can be either a SLES 12, SLES 15, or Centos 7 based ISO, and the path can be relative
or absolute. The ISO argument can also be a URL, which will be downloaded into
the download directory before bringing up the cluster.

There are some optional arguments you can pass to the command:

    --backends=[0-253]            The number backends to create. Default: 0
    --fqdn=FQDN                   The FQDN of the frontend. Default: cluster-up-frontend.localdomain
    --name=NAME                   The name to uniquely identify this cluster. Default: cluster-up-RRRRRRRR
    --download-dir=DIRECTORY      The directory to store installer ISOs. Default: '.'
    --use-the-src-dir=DIRECTORY   The directory will be mounted and symlinked into the frontend.
    --export-frontend             Export the frontend as a vagrant box with the same name as the STACK_ISO
    --forward-ports=SRC:DST[,...] Comma separated list of ports to forward.
    --no-pxe                      Created backends using the minimal OS box.

You can also specify the following flags, which will switch cluster-up to create
the second interface to a bridge interface on the VM host. If you specify a bridged
interface, then no backends will be automatically created, as they rely on host only
networking. Instead, you can create your own backends over the bridged interface.

    --bridge=INTERFACE            Bridge interface on the host. Default: Use host only networking
    --ip=IP_ADDRESS               IP Address for the bridge network. Default: Use DHCP
    --netmask=NETMASK             The netmask for the bridge network. Default: 255.255.255.0
    --gateway=GATEWAY_ADDRESS     Gateway address for the bridged interface.
    --dns=DNS_ADDRESS[,DNS2]      Comma separated list of DNS servers.

The script will create a generic OS frontend box in Virtualbox or KVM, install
Stacki on it, then pxe-boot the number of backends requested (None by default) and
install an OS on them from the Stacki frontend.

Once all of that is done, you can ssh into the frontend as `root` with the command:

    vagrant ssh frontend

The backends are named 'backend-0-N' where N is the number of backends
created, starting at zero. So, to ssh into the backend-0-0 you would run:

    vagrant ssh backend-0-0

When you are done with the cluster, you can destroy it with the command:

    ./cluster-down.sh

## Examples
The simplest invocation of the tool is to create a cluster with the frontend
and no backends. That command would simply look like:

    ./cluster-up.sh stacki-05.02.04.00-redhat7.x86_64.disk1.iso

If you want a handful of backends, assign your frontend a specific FQDN, and to
fetch the ISO from a URL, the comand would look like:

    ./cluster-up.sh \
        --backends=3 \
        --fqdn=stacki-frontend.example.com \
        http://example.com/stacki-05.02.04.00-redhat7.x86_64.disk1.iso

You can create a development environment, with a checkout of the Stacki code
repository mapped into it, by using the `--use-the-src-dir` flag like so:

    ./cluster-up.sh --use-the-src-dir=~/Code/stacki \
        http://example.com/stacki-05.02.04.00-redhat7.x86_64.disk1.iso

A more complicated use of the tool is to create a Stacki frontend that can
provision physical backends. For this, you need to have a bridged network
interface set up in either KVM or Virtualbox.

You then specify all your
bridge network infomation via flags, such as:

    ./cluster-up.sh \
        --fqdn=sd-stacki-147.labs.teradata.com \
        --bridge=br1 \
        --ip=10.25.250.147 \
        --gateway=10.25.250.254 \
        --dns=153.64.251.200 \
        stacki-05.02.04.00-sles12.x86_64.disk1.iso

It is a little annoying that in Virtualbox, at least under the Mac, the bridge
interface names are a little unwieldy, and you have to specify the entire name,
or else it will prompt you several times to select your bridge.

So, under Virtualbox, your command might look like:

    ./cluster-up.sh \
        --fqdn=sd-stacki-147.labs.teradata.com \
        --bridge="en8: Belkin USB-C LAN" \
        --ip=10.25.250.147 \
        --gateway=10.25.250.254 \
        --dns=153.64.251.200 \
        stacki-05.02.04.00-sles12.x86_64.disk1.iso

## Hooks
Customization scripts can be added into a set of folders under the `hooks` folder, to be
invoked at various points in the `cluster-up.sh` process. The hook scripts must have the
execute bit set.

The various hook run points are:
- **pre-cluster-up** - After parsing the command arguments but prior to anything else.

- **pre-frontend** - Right before vagrant is used to start the frontend VM.

- **post-frontend** - After the installation reboot for the frontend.

- **pre-export** - Before the vagrant box is exported but after the frontend has been set
up to install backends. _Only ran if the `--export-frontend` flag is set._

- **post-export** - After the vagrant box has been exported and the frontend has been
restarted. _Only ran if the `--export-frontend` flag is set._

- **pre-backends** - After discovery has been started on the frontend but before any backends
have been started by vagrant. _Only ran if backends are to be provisioned._

- **post-backends** - After all backends have been provisioned but before discovery has been
disabled on the frontend. _Only ran if backends are to be provisioned._

- **post-cluster-up** - Right before the `cluster-up.sh` exits and after the success message
has been printed out to the terminal.
