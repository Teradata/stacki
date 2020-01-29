# Adding support for new distros in stacki

This is a rough outline of the steps needed to add support for a new distro to stacki.  In particular, this is the process that was followed as support was added for SLES 15.  Obviously, adding support for a different distro family (say, Ubuntu) would be a larger effort.

## prepare the build environment

Grab relevant media - for sles15: installer and packages isos.
install git (on sles, this is in a repo in the packages iso)
grab stacki src

In general, bootstrap needs development tools, iso building tools, apache, and package repo tools

## get make bootstrap's first stage working

this will likely involve teaching stacki how to identify the build-host OS.

You may need to edit:

common/src/stack/build/build/bin/os
common/src/stack/build/build/bin/os-release

Find the bootstrap.mk for the OS ($OS/bootstrap.mk), which installs packages and metapackages.
The names of these change between releases, so you may need to add conditionals here.

## get make bootstrap's second stage working

It is very likely the Makefile in common/src/foundation/python/ will need to be updated.

## get make working

This involves tracking down missing dependencies that might be needed for python packages or other things in foundation

## you have an iso.  make frontend-install.py work with it

self.os detection in command's megainit may need to be updated.  Likewise, the OS and os.version detection in frontend-install.py.

Additionally, you need to edit code that generates the const attr for `os.version` which is used in the graph for backends and the frontend.  As of this writing, that detection is based on a hard-coded whitelist of pallets in each host's box.  The code itself lives in: common/src/stack/command/stack/commands/list/attr/plugin_host_intrinsic.py

Once you have os.version, you'll need to find the places in the graph which are os/version dependent, and make decisions there.  Sometimes this will be package renames, other more painful changes may mean different functionality or script logic.

