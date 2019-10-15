![alt tag](logo.png)


# Stacki 5.4

Go [here](https://github.com/Teradata/stacki/releases/tag/stacki-5.4) for more details and downloads.

New release:
* [Documentation for Stacki 5.x](https://github.com/Teradata/stacki/wiki)

Previous release:
* [Documentation for Stacki 4.0](https://github.com/Teradata/stacki-documentation-4.x/wiki)

## Mailing list and Slack

Join the GoogleGroups  [mailing list](https://groups.google.com/forum/#!forum/stacki)

Longer, detailed solutions get posted to the mailing list.

Join the [Slack Channel](https://join.slack.com/t/stacki/shared_invite/enQtMzEwOTIzMTIyOTk1LWMzMGJhZGUxNDc2ODczMDM1ODkwYmM5MGZlOWUxMTVmMDQ5NzZhZmVmNDEwZDIwZWY3NzVlOGM0NjIxMjJiYjY)

Lots of things happen here. Smart things. Funny things. Questions whose answer is usually 'RTFM' except we know how to say it nicely. Well, some of us do.

# What is Stacki?

Stacki is a CentOS/RHEL/SLES bare metal install tool that can take your servers from bare hardware (or virtual hardware) to working Linux - ready to install applications. Stacki does this at scale, so deploying 1000+ servers is no more complex than deploying one. Advanced users can use Stacki to install applications (Hadoop, OpenStack, HPC etc.). Stacki has a long history, and is in use at some of the most demanding organizations in the world.

The Stacki default installation process will bring bare metal infrastructure (or VMs) to a ping and a prompt. The frontend machine has password-less SSH access to the backend machines on first boot, and the repositories on the frontend act as repositories for all backend machines. All machines will be at the latest kernel and RPM revisions of the OS and installed applications.

## I know whatever, what does Stacki do?

* Install OS.
* Configure OS.
* Configure RAID controllers and partitioning (both customizable). This means you never have to touch a monitor and keyboard to customize the RAID configuration on machines, not even once. Set-up the RAID controller configuration via spreadsheet, ingest it, and install. The RAID will be configured on first installation with no human interaction required.
* Configure networking. This includes configuring multiple network interfaces, multiple network types: IB, 10G, 1G, and authenticated SSH password-less access at boot.
* Machines are disposable. Everything is built from the ground up programmatically. Recovering from disasters is a simple rebuild.
* Data is preserved across reinstalls.
* Integrates with DevOps tools: Ansible, Puppet, Chef, Salt.
* Leave you to be productive, to focus on more interesting problems.
