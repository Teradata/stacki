# Yes! Ubuntu!

You asked, we listened, and now we're releasing Stacki Ubuntu into the open source Stacki tree. You can now automatically install Ubuntu via a preseed network install to backend machines from a Stacki frontend. The only thing you have to do is prep your frontend.

# Building a better preseed

Using preseed is one of the most painful installation mechanisms I have ever used. No, really. You have to do the most horrific machinations to configure multiple interfaces, multiple disks, have a debug console, and the list goes on.

So getting Ubuntu on a cluster of machines that need to be absolutely consistent, at scale, just seems like something not very many people do. (For example, no one in the enterprise ever asked us if we could install Ubuntu so they could do big data, cloud, or HPC. No.One.Ever.)`

Our goal with any OS in a cluster is to install it with the same speed and features we do with CentOS. This realease brings us closer to that goal. This release is not feature complete, but it is feature completer than it was initially.

To make this work, we needed to write into the installer, which limits the versions of Ubuntu we can do. We only support LTS releases, so right now only Xenial (16.04) and the minor versions (1,2,3) are supported. We will update when Ubuntu releases a new LTS version. We do not have plans to go backwards unless there is a ground swell of requests from the community. Since no one ever reads this, that likely won't happen. 

## New Features
- Configure multiple static interfaces.
- Partitioning of multiple disks using spreadsheets. 
- An sshd running during install that allows you to debug.
- XFS available for all filesystems.

# Requirements
- A Stacki frontend with Stacki 4.0. It likely won't work on anything less than 4.0.
- stacki-ubuntu-frontend pallet
- stacki-ubuntu-backend pallet
- Ubuntu-Server Xenial iso, 16.04.1,2, or 3. (But you should use 16.04.3 since it has the latest security releases.)
 

## Setup
Download stacki-ubuntu-pallets

```
wget https://teradata-stacki.s3.amazonaws.com/release/stacki/4.x/stacki-ubuntu-frontend-4.0_20170414_c4aff2a-7.x.x86_64.disk1.iso

md5 = 55ba30652556994860d5f492cba48939

wget https://teradata-stacki.s3.amazonaws.com/release/stacki/4.x/stacki-ubuntu-backend-4.0_20170414_c4aff2a-7.x.x86_64.disk1.iso

md5 = 694ff792eabf27fbdded062316e174b3
```

You have to add and run the stacki-ubuntu-frontend pallet before adding the stacki-ubuntu-backend pallet or the Ubunto-Server iso. So let's do that:

Add stacki-ubuntu frontend pallet:

	# stack add pallet stacki-ubuntu-frontend-4.0_20170414_c4aff2a-7.x.x86_64.disk1.iso
	# stack enable pallet stacki-ubuntu-frontend
	# stack run pallet stacki-ubuntu-frontend | bash

Now we can safely add the stacki-ubuntu-backend pallet:

	# stack add pallet stacki-ubuntu-backend-4.0_20170414_c4aff2a-7.x.x86_64.disk1.iso

Add an Ubuntu iso. You can find the downloads page for version 16.04.2 which I am using, here: http://releases.ubuntu.com/16.04.3/ubuntu-16.04.3-server-amd64.iso

	#  stack add pallet ubuntu-16.04.2-server-amd64.iso

Add an Ubuntu box (can be named anything but the "os=ubuntu" must be given)

	# stack add box ubuntu-xenial os=ubuntu

Add the Ubuntu pallets to the ubuntu box.

	# stack enable pallet stacki-ubuntu-backend Ubuntu-Server box=ubuntu-xenial


Run the frontend pallet again. (Trust me on this.)

	# stack run pallet stacki-ubuntu-frontend | bash

Assign nodes to the ubuntu box

	# stack set host box backend box=ubuntu-xenial

Set the installaction

	# stack list bootaction | grep ubuntu
	# stack set host installaction backend action=ubuntu.xenial.16.04.3

Install

	# stack set host boot backend action=install

Reboot the backend nodes

## What you get

### Partitions
Default installation gives you /, /var, swap, and /state/partition1. To use a different partitioning scheme, use a storage partition spreadsheet. Like this:

```
# cat myparts.csv

NAME,DEVICE,MOUNTPOINT,SIZE,TYPE,PARTID,OPTIONS
backend,sda,swap,16000,swap,2,
,sda,/,20000,ext3,1,
,sda,/var,25000,ext3,3,
,sda,/state/partition1,0,ext3,4,--primary=1 --mnt_options="async auto" --fs_options="nosuid"
,sdb,/hadoop1,20000,xfs,1,--mnt_options="async auto"
,sdb,/hadoop2,5000,xfs,2, --fs_options="nosuid"
,sdb,/hadoop3,0,xfs,3,
```

And then load it:

```
stack load storage partition file=mypartitions.csv
```

And then set nukedisks and reinstall to get the new partitioning:

```
stack set host attr backend-0-0 attr=nukedisks value=true

stack set host boot backend-0-0 action=install

*reboot*
```

### Network

If you have more than one interface and more than one network on backend nodes, they will be automatically plumbed. 

For example:

```
[root@ubudemo ~]# stack list network
NETWORK ADDRESS  MASK          GATEWAY  MTU   ZONE       DNS   PXE
natnet  10.0.2.0 255.255.255.0 10.0.2.1 1500  jkloud.com False False
private 10.1.1.0 255.255.255.0 10.1.1.1 1500  local      False True
```

And:

```
[root@ubudemo ~]# stack list host interface backend-0-0
HOST        INTERFACE DEFAULT NETWORK MAC               IP         NAME        MODULE VLAN OPTIONS CHANNEL
backend-0-0 eth0      True    private 08:00:27:61:52:2e 10.1.1.254 backend-0-0 ------ ---- -------
backend-0-0 eth1      ------- natnet  08:00:27:b2:c7:65 10.0.2.254 ----------- ------ ---- -------
```

Will show up on the backend like this:

```
root@backend-0-0:~# ls /etc/network/interfaces.d/
eth0.cfg  eth1.cfg

root@backend-0-0:~# ifconfig
eth0      Link encap:Ethernet  HWaddr 08:00:27:61:52:2e
          inet addr:10.1.1.254  Bcast:10.1.1.255  Mask:255.255.255.0
          inet6 addr: fe80::a00:27ff:fe61:522e/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:103 errors:0 dropped:0 overruns:0 frame:0
          TX packets:76 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:12055 (12.0 KB)  TX bytes:11371 (11.3 KB)

eth1      Link encap:Ethernet  HWaddr 08:00:27:b2:c7:65
          inet addr:10.0.2.254  Bcast:10.0.2.255  Mask:255.255.255.0
          inet6 addr: fe80::a00:27ff:feb2:c765/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:0 (0.0 B)  TX bytes:648 (648.0 B)
```

### Debugging

To turn on debugging, set the debugging attribute:

```
stack set host attr backend-0-0 attr=debug value=true
```

This stops the installation right before reboot so you can log in and see what happened, is happening, etc. To log-in, from the frontend:

```
ssh -p 2200 backend-0-0
```

To finish the installation execute "rm -f /tmp/debug"

You can log-in without setting the "debug" flag to watch the install happen through logs in /tmp. The installation will continue until it's finished and reboot. 

## Next Release

A bunch of stuff should be done to make Ubuntu install with all 
the perks and superdoublechocolateawesomeness we use when 
installing RHEL/CentOS. 

Stacki 5.0 will come out in the next couple of months, and we expect to make Ubuntu feature commensurate with that release. 

This will include:

- Parallel formatting of disk.
- Ludicrous installer - peer-to-peer sharing of files during and after installation
- Putting in https!
- Controller configuration.
- Discovery mode.
- XML file fixes to obviate the need to be a preseed expert.

### Questions you're going to ask that I have no idea about:

You: Does this work with Ubuntu Desktop? 
Me: No it doesn't. This is a cluster installer, not a desktop installer. No, it will not work with Ubuntu Desktop, ever.

You: Does this work with Debian?
Me: Not yet. Shouldn't be hard. Maybe soon. Maybe not.

You: Does this work on my Raspberry Pi?
Me: Really? Seriously? (Actually, we're more likely to do this than Ubuntu Desktop, so there is a chance...)

You: Can I mirror the entire Ubuntu repo?
Me: Yes. It's a horror and you have to have a big disk. If you read this far, ask on the Stacki Slack channel, and I'll give you an answer/rant. You don't get one without the other.

You: Can you add X so I can do Y because it would be awesome to show my Zs? 
Me: No, we no longer offer professional services, and you're using Ubuntu so you clearly weren't going to pay for that anyway. 

BUT! You can do it! It's Open Source and we're happy to help, just ask on the Slack channel or googlegroups list and we'll get you going. 
