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




