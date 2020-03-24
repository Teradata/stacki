# Automated Vagrant based build process

You need to have [Vagrant](https://www.vagrantup.com/) installed, and either
[VirtualBox](https://www.virtualbox.org/) or Libvirt/KVM. If using Libvirt/KVM, you also need to
[install the vagrant-libvirt plugin](https://github.com/vagrant-libvirt/vagrant-libvirt#installation)
and NFS server on the host.

Outside of the Teradata network, only the "redhat7" platform (CentOS based) can be built.

## Setup

Set the following REQUIRED environment variable:

* **PLATFORM** - The platform to build for. One of: "redhat7", "sles15", "sles12", or "sles11".

Optional environment variables:

* **ISOS** - Folder where the required ISOs for the build process will be downloaded. This can be an absolute path or one relative to the Vagrantfile. Defaults to "." (the `tools/iso-builder/` directory containing the Vagrantfile).

* **IS_RELEASE** - Set to "true" if the date and SHA shouldn't be embedded in the file name.

* **OS_PALLET** - If set to a filename during a "redhat7" platform build, a StackiOS ISO will be generated along with the normal Stacki ISO. The OS pallet needs to already be downloaded into the folder specified in the ISOS environment variable.

* **PYPI_CACHE** - Set to "true" to have the build script use our internal Stacki Builds PyPI cache, which is needed to build the "sles11" platform.

* **UPDATE_LOCKFILE** - Set to "true" to regenerate the poetry.lock file for the Python modules

## Usage

Set the required environment variables, then change into the `tools/iso-builder` folder and run: `vagrant up`

This will bring up a VM and build the pallet, which will end up in the root of the project.

Run `vagrant destroy -f` to clean up the iso-builder VM.


## Example

1. Change into the `tools/iso-builder` directory
2. Run: `PLATFORM='redhat7' vagrant up`
3. Once it finishes, you have your ISO. Clean up: `vagrant destroy -f`
