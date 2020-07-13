# Start from a fresh debian build

Use debian-10.4.0-amd64-DVD-1.iso

* unselect all packages
* choose "use network mirror"

# After Installation

Login on the console as root

* edit /etc/apt/sources.list

comment out line mentioning dvd media so we only use remote repos

* add software

apt install openssh-server
apt install git
apt install make

* edit /etc/ssh/sshd.conf
add "PermitRootLogin yes"

logout and ssh back in as root

# Building Stacki

* git clone git@github.com:Teradata/stacki.git
* git checkout -b feature/debian origin/feature/debian
* cd stacki
* make bootstrap

logout and login in again (as in follow the instructions after make finishes)

* make bootstrap
* make
* ls build-stacki-feature_debian

you should see an .iso file here

# Barnacle

You can do this on the same host that built the iso (in fact that's
the only thing that has been tested).

From the top of the stacki source tree

* ip address
* tools/fab/frontend-install.py --stacki-iso build-stacki-feature_debian/*.iso

Enter in the network info, password, etc

Next copy over the debian media that you intalled from and add that as a pallet

* stack add pallet debian-10.4.0-amd64-DVD-1.iso

# Add a Backend

Do the standard stacki stuff to add a backend into the database, set
its boot action to install and PXE boot it.

The debian/nodes/backend.xml file is the only node if the backend's
graph the idea is to get this right to a basic config and then start
hooking on other node file. The stack:native tag should be used for
most of the really debian specific ideas. Support needs to be added
for stack:script and stack:packages.


