![alt tag](logo.png)


# There's a new release!

Stacki 5.0 was released on 11/30/2017. Go [here](https://github.com/Teradata/stacki/releases/latest) for more details and downloads. Installing is similar to previous versions; however, documents are lagging, just so's you know.


* [documentation](https://github.com/StackIQ/stacki/wiki)
* [mailing list](https://groups.google.com/forum/#!forum/stacki)

# Why Bare Metal Provisioning?
 
Automation and consistency across Linux infrastructure is hard. Our goal is to make Linux installations of heterogeneous hardware across 10s to 1000s of machines fast, flexible, and absolutely consistent.
The Stacki default installation process will bring bare metal infrastructure (or VMs) to a ping and a prompt. The frontend machine has password-less SSH access to the backend machines on first boot, and the repositories on the frontend act as YUM repositories for all backend machines. All machines will be at the latest kernel and RPM revisions of the OS and installed applications.

Stacki initial installations are relatively fast and simple, but may not completely reflect site-specific desired state. Configuration can be layered on using advanced features to customize local environments. The speed of installation/reinstallation Stacki provides allows convergence to a known/desired configuration of resources that reflect local needs. Deployed across the infrastructure, you’ve just made the complex simple and repeatable for existing or new infrastructure.

# What is Stacki?

Stacki is a CentOS/RHEL/Ubuntu bare metal install tool that can take your servers from bare hardware (or virtual hardware) to working Linux, ready to install applications. Stacki does this at scale, so deploying 1000+ servers is no more complex than deploying one. Advanced users can use Stacki to install applications (Hadoop, OpenStack, HPC etc.). Stacki has a long history, and is in use at some of the most demanding organizations in the world.
 
## What does Stacki do?

* Configure RAID controllers and partitioning (both customizable). This means you never have to touch a monitor and keyboard to customize the RAID configuration on machines, not even once. Set-up the RAID controller configuration via spreadsheet, ingest it, and install. The RAID will be configured on first installation with no human interaction required.
* Install OS.
* Configure OS.
* Configure networking. This includes configuring multiple network interfaces, multiple network types: IB, 10G, 1G, and authenticated SSH password-less access at boot.
* Leave you to be productive, to focus on more interesting problems.

With Stacki, machines are disposable. Everything is built from the ground up programmatically so recovering from disasters just means rebuilding your servers.
Machines are disposable but data is not. After the initial installation, data is preserved across reinstalls. Data drives are reformatted only by deliberate action. A reinstall is a refresh of the OS and/or application software while data on disk is preserved.
Stacki delivers certainty. If you’re configuring individual machines on a daily basis without automation, you’re losing. Our goal is to keep you from having to configure individual servers and always knowing the answer to: “What state are my servers in?”
Once your servers are installed with Stacki, augment them with your favorite configuration toolset – be it shell scripts, Salt, Chef, Puppet, CFEngine, Ansible, or homegrown – you don’t have throw away work already done. Although, once you see what it can do, some of that post-install configuration management may be easily replaced during installation.

# Downloads

## Stacki for CentOS/RHEL version 5.0


### Older Downloads
Stacki is CentOS first, this is where all of our develop starts.  You should start here as well before wandering of into Ubuntu and Pi land.


### [Stacki 4.0 CentOS 6.x](http://stacki.s3.amazonaws.com/public/pallets/4.0/open-source/stackios-4.0-6.x.x86_64.disk1.iso?id=%22download_iso6_button%22&source=%22https://www.stackiq.com/downloads/%22&page=%22/downloads/%22)

### [ Stacki 4.0 CentOS 7.3](http://stacki.s3.amazonaws.com/public/pallets/4.0/open-source/stackios-4.0_c4aff2a-7.x.x86_64.disk1.iso?id=%22download_iso7_button%22&source=%22https://www.stackiq.com/downloads/%22&page=%22/downloads/%22)


## Stacki for Ubuntu (Trusty, Wily, Xenial, or Yakkety)

You asked, we listened, and now we’re releasing Stacki Ubuntu into the open source Stacki tree. You can now automatically install Ubuntu via a preseed network installation to boot backend machines from a Stacki frontend. The only thing you have to do is prep your frontend.
It's latest release now does multi-disk partitioning and multiple network interface configuration. We are starting to make a better preseed.
In the meantime, follow the [GitHub README](https://github.com/Teradata/stacki-ubuntu/blob/master/README.md) and the requirements below to get started.

### Requirements:

* A Stacki frontend with Stacki 4.0. It likely won’t work on anything less than 4.0.
* [Stacki-ubuntu-frontend Pallet ](https://teradata-stacki.s3.amazonaws.com/release/stacki/4.x/stacki-ubuntu-frontend-4.0_20170414_c4aff2a-7.x.x86_64.disk1.iso) (MD5 = 55ba30652556994860d5f492cba48939)
* [Stacki-ubuntu-backend Pallet](https://teradata-stacki.s3.amazonaws.com/release/stacki/4.x/stacki-ubuntu-backend-4.0_20170414_c4aff2a-7.x.x86_64.disk1.iso) (MD5 = 694ff792eabf27fbdded062316e174b3)
* Ubuntu-Server iso from Xenial, minor version 1,2, or 3 (e.g., ubuntu-16.04-server-amd64.iso)

## Stacki Ace (CentOS 7 for ARM)

Stacki Ace is the new open-source port of Stacki to the Raspberry Pi providing the quickest way to go from one Raspberry Pi with nothing installed to a fully functioning cluster. There is a “Stacki” Pallet that is built from the Stacki open-source repository and there is a new “Stacki-ace” Pallet that we created to specifically support the Pi.

Once you have the required Raspberry Pis and the hardware, download the stacki-centos.img and ISOs (MD 5 checksum) below, and follow the [GitHub README](https://github.com/Teradata/stacki-ace/blob/master/README.md) to get started.

### Hardware Requirements

#### Frontend
* [Raspberry Pi 3 Model B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
* MicroSD card with at least 8 GB of storage

#### Backend

* [Raspberry Pi Model B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
* MicroSD card with at least 2 GB of storage

All users should start with the following link to ‘stacki-centos.img’:

* [Stacki-centos.img](http://stacki.s3.amazonaws.com/public/pallets/4.1/open-source/ace/stacki-centos.img?id=%22download_stackicentosrpimg_link%22&source=%22https://www.stackiq.com/downloads/%22&page=%22/downloads/%22)

After you build your frontend Pi, copy the following ISOs to your frontend:

* [OS-7.3-7 ISO](http://stacki.s3.amazonaws.com/public/pallets/4.1/open-source/ace/os-7.3-7.x.armv7hl.disk1.iso?id=%22download_os737rpiso_link%22&source=%22https://www.stackiq.com/downloads/%22&page=%22/downloads/%22)
* [Stacki-4.1 ISO](http://stacki.s3.amazonaws.com/public/pallets/4.1/open-source/ace/stacki-4.1-7.x.armv7hl.disk1.iso?id=%22download_stacki4isorp_link%22&source=%22https://www.stackiq.com/downloads/%22&page=%22/downloads/%22)
* [Stacki-ace-4.1 ISO](http://stacki.s3.amazonaws.com/public/pallets/4.1/open-source/ace/stacki-ace-4.1-7.x.armv7hl.disk1.iso?id=%22download_stackiace4iso_link%22&source=%22https://www.stackiq.com/downloads/%22&page=%22/downloads/%22)

Download and execute frontend-install.py

* [Frontend-install.py](http://stacki.s3.amazonaws.com/public/pallets/4.1/open-source/ace/frontend-install.py)



