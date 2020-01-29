# Adding support for new distros in stacki

This is a rough outline of the steps needed to add support for a new distro to stacki.  In particular, this is the process that was followed as support was added for SLES 15.  Obviously, adding support for a different distro family (say, Ubuntu) would be a larger effort.

## Get a working Frontend on the new version

### prepare the build environment

Grab relevant media - for sles15: installer and packages isos.
install git (on sles, this is in a repo in the packages iso)
grab stacki src

In general, bootstrap needs development tools, iso building tools, apache, and package repo tools

### get make bootstrap's first stage working

this will likely involve teaching stacki how to identify the build-host OS.

You may need to edit:

common/src/stack/build/build/bin/os
common/src/stack/build/build/bin/os-release

Find the bootstrap.mk for the OS ($OS/bootstrap.mk), which installs packages and metapackages.
The names of these change between releases, so you may need to add conditionals here.

### get make bootstrap's second stage working

It is very likely the Makefile in common/src/foundation/python/ will need to be updated.

### get make working to build an iso

This involves tracking down missing dependencies that might be needed for python packages or other things in foundation

### you have an iso.  make frontend-install.py work with it

self.os detection in command's megainit may need to be updated.  Likewise, the OS and os.version detection in frontend-install.py.

Additionally, you need to edit code that generates the const attr for `os.version` which is used in the graph for backends and the frontend.  As of this writing, that detection is based on a hard-coded whitelist of pallets in each host's box.  The code itself lives in: common/src/stack/command/stack/commands/list/attr/plugin_host_intrinsic.py

Once you have os.version, you'll need to find the places in the graph which are os/version dependent, and make decisions there.  Sometimes this will be package renames, other more painful changes may mean different functionality or script logic.

## Get working backends for the new version

### Add the initrd

This is going to be highly distro-specific.  Copy over the initrd and kernel from the media, typically to $OS/src/stack/images.  Determine how to patch the installer with stacki-specific bits (this is typically via a squashfs and/or a repacked initrd).  There are a list of packages (some stacki, some not) that we unpack and add to this filesystem - see `sles/src/stack/images/SLES/sles15/15sp1/images.mk` or `sles/src/stack/images/7.6.1810/updates.img/version.mk` or grep for `OVERLAY.PKGS` or `YUMLIST`.  The new initrd/squashfs may need to be signed (as in sles).

Once that is in place, you'll want to ensure it is installed on the stacki system at the time the pallet is added.  The recent way we've handled this is via pallet_hooks.

### Update distro-specific portions of the database data/command line

Update bootactions to point to thew new initrd, backend node xml, and backend partitioning.

### Fix/update all tests, the test framework, and cluster-up

some tests may assume the frontend will be running a given version of a distro - these need to be updated.  If you haven't built vagrant boxes for the new distro (bless your heart) you'll need to do so now and plumb these tools into them.
