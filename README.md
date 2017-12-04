![alt tag](logo.png)


# There's a new release!

Stacki 5.0 was released on 11/30/2017. Go [here](https://github.com/Teradata/stacki/releases/latest) for more details and downloads. Installing is similar to previous versions; however, documents are lagging, just so's you know.


New release:

* [Documentation for Stacki 5.0](https://github.com/Teradata/stacki/wiki)

Previous release:
* [Documentation for Stacki 4.0](https://github.com/Teradata/stacki/wiki)

Join the mailing list. 

Longer detailed solutions get posted to the mailing lis. 

* [Mailing list](https://groups.google.com/forum/#!forum/stacki)

Join the Slack Channel:

Lots of things happen here. Smart things. Funny things. Questions whose answer is usually 'RTFM' but nicely said. 

Once on googlegroups, email a request to be added.

# What is Stacki?

Stacki is a CentOS/RHEL/Ubuntu bare metal install tool that can take your servers from bare hardware (or virtual hardware) to working Linux - ready to install applications. Stacki does this at scale, so deploying 1000+ servers is no more complex than deploying one. Advanced users can use Stacki to install applications (Hadoop, OpenStack, HPC etc.). Stacki has a long history, and is in use at some of the most demanding organizations in the world.

The Stacki default installation process will bring bare metal infrastructure (or VMs) to a ping and a prompt. The frontend machine has password-less SSH access to the backend machines on first boot, and the repositories on the frontend act as YUM repositories for all backend machines. All machines will be at the latest kernel and RPM revisions of the OS and installed applications.
 
## I know whatever, what does Stacki do?

* Configure RAID controllers and partitioning (both customizable). This means you never have to touch a monitor and keyboard to customize the RAID configuration on machines, not even once. Set-up the RAID controller configuration via spreadsheet, ingest it, and install. The RAID will be configured on first installation with no human interaction required.
* Install OS.
* Configure OS.
* Configure networking. This includes configuring multiple network interfaces, multiple network types: IB, 10G, 1G, and authenticated SSH password-less access at boot.
* Leave you to be productive, to focus on more interesting problems.
* Machines are disposable. Everything is built from the ground up programmatically. Recovering from disasters is a simple rebuild.
* Data is preserved across reinstalls.
* Integrates with DevOps tools: Ansible, Puppet, Chef, 




