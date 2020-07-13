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


