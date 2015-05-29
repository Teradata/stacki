#!/bin/sh
#
# These functions are used to help bootstrap a new or updated Roll into an
# existing frontend.  To bootstrap we cannot use pylib or even python XML
# parsing.  This script starts out as shell code but it generates some
# simple python code to handle the installation of required packages.
#
# $Id$
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@
#
# $Log$
# Revision 1.2  2010/09/07 23:53:05  bruno
# star power for gb
#
# Revision 1.1  2010/06/22 21:07:44  mjk
# build env moving into base roll
#
# Revision 1.13  2009/05/22 07:04:24  anoop
# Big fix in bootstrap-functions.sh. Use "rocks list node xml" instead of kpp
#
# Revision 1.12  2009/05/01 19:07:15  mjk
# chimi con queso
#
# Revision 1.11  2008/10/18 00:56:07  mjk
# copyright 5.1
#
# Revision 1.10  2008/03/06 23:41:50  mjk
# copyright storm on
#
# Revision 1.9  2007/10/25 05:34:41  anoop
# Now called sunos, not solaris
#
# Revision 1.8  2007/06/19 21:40:31  mjk
# do not use NAME in roll-profile.mk
#
# Revision 1.7  2006/12/02 01:53:02  anoop
# Rolls.mk changed a little bit to accomadate Solaris
#
# bootstrap-functions.sh changed to accomadate solaris. The python code that is
# generated is now a part of install_os_package_linux rather than just install_os_package
#
# Revision 1.6  2006/09/11 22:48:04  mjk
# monkey face copyright
#
# Revision 1.5  2006/08/10 00:10:20  mjk
# 4.2 copyright
#
# Revision 1.4  2006/02/07 22:00:13  mjk
# add support for other rolls (not just base)
#
# Revision 1.3  2006/01/17 03:46:38  mjk
# uncommented real code (was still debugging)
#
# Revision 1.2  2006/01/17 03:45:27  mjk
# bootstrap works
#
# Revision 1.1  2006/01/17 00:11:37  mjk
# *** empty log message ***
#

BOOTSTRAP_PY=bootstrap.py

##
## Linux
##

function install_redhat() {
	find /usr/src/redhat/RPMS -name "$1-[0-9]*.*.rpm" \
		-exec rpm -Uhv --force --nodeps {} \;
	find RPMS -name "$1-[0-9]*.*.rpm" \
		-exec rpm -Uhv --force --nodeps {} \;
}

function compile_redhat() {
	(cd src/$1; gmake pkg)
}

function install_os_packages_redhat() {
	for pkg in `stack list node xml $1 basedir=$PWD |	\
		kgen --section packages |			\
		grep "^[a-zA-Z]"`; do				\
		echo "needed.append(\"$pkg\")" >> $BOOTSTRAP_PY;\
	done

	cat >> $BOOTSTRAP_PY << 'EOF'

# At this point we should have pylib so we can start doing things
# the easy way.  Build a local distribution and install all the OS
# packages needed.

import sys
import os
import stack.app
import stack.roll

class App(stack.app.Application):
	def run(self):
		list = []
		for e in needed:
			if e not in installed and e not in ignored:
				list.append(e)
		dist = stack.roll.Distribution(self.getArch())
		dist.generate('--notorrent --with-rolls-only')
		for e in list:
			if dist.getRPM(e):
				for pkg in dist.getRPM(e):
					pkg.installPackage(os.sep)

app = App(sys.argv)
app.parseArgs()
app.run()
EOF
	/opt/stack/bin/python $BOOTSTRAP_PY
	rm -rf rocks-dist
	rm $BOOTSTRAP_PY
}


##
## Solaris
##

function install_sunos() {
	echo $1
	pkg_name=`find PKGS -name "ROCKS$1" -type d | xargs basename`;
	yes | pkgadd -d PKGS $pkg_name;
#		-exec pkginfo -d PKGS {} \;
}

function compile_sunos() {
	(cd src/$1; gmake pkg)
#	echo $1
}

function install_os_packages_sunos() {
	/bin/true
}

##
## MacOSX
##

function install_macosx() {
	echo $1
}

function compile_macosx() {
	echo $1
}

function install_os_packages_macosx() {
	/bin/true
}


##
## Generic Methods
##

function install() {
	echo "###"
	echo "### install $1"
	echo "###"
	echo "installed.append(\"$1\")" >> $BOOTSTRAP_PY
	install_`./_os` $1
}


function compile() {
	echo "###"
	echo "### compile $1"
	echo "###"
	compile_`./_os` $1
}

function ignore_os_package() {
	echo "ignored.append(\"$1\")" >> $BOOTSTRAP_PY
}

# This code is really redhat dependent and will be until pylib abstracts
# away from kickstart files and redhat distributions. 

function install_os_packages() {
	echo "###"
	echo "### install os packages"
	echo "###"
	echo "needed = []" >> $BOOTSTRAP_PY
	install_os_packages_`./_os` $1
}


function compile_and_install() {
	compile $1
	install $1
}

function init() {
	gmake clean
	gmake Rolls.mk
	echo "installed = []" >> $BOOTSTRAP_PY
	echo "ignored   = []" >> $BOOTSTRAP_PY
}

init

