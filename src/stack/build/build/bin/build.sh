#!/bin/bash

BASE="roll-core,6.3 roll-base,6.3 roll-ganglia,3.3.7 roll-kernel,6.3 roll-web-server,6.3"

# BIGDATA="roll-hadoop-base roll-hadoop-cloudera roll-hadoop-mapr"
BIGDATA="roll-hadoop-base,1.1.1.16 roll-hadoop-mapr,2.0.0.15153GA"

# CLOUD="roll-cloudstack"
CLOUD=""

# ALU="roll-alu roll-cloudstack"
ALU=""

# VENDOR="roll-dell roll-hp"
VENDOR=""

# HPC="roll-intel-developer roll-mlnx-ofed roll-moab roll-sge roll-uge roll-cuda roll-hpc"
HPC=""

CENTOS="CentOS,6.3"
# OS=""
OS="roll-os,6.3.`date +%Y%m%d`"


ROLLS="$CENTOS $BASE $BIGDATA $CLOUD $ALU $VENDOR $HPC $OS" 

RELEASE=stack1
CODENAME=pumpkin

METABASE="core*iso base*iso ganglia*iso kernel*iso web-server*iso"
METAOS="os*disk1*iso os*disk2*iso"

BIGDATAVERSION=2.0
METABIGDATA="hadoop*iso"

CLOUDVERSION=1.0
METACLOUD="cloudstack*iso"

HPCVERSION=3.0
METAHPC="hpc*iso cuda*iso sge*iso mlnx-ofed*iso"



meta() {
	(cd ISOS ; \
		stack create pallet name=StackIQEnterpriseData \
			version=$BIGDATAVERSION-$RELEASE \
			$METABASE $METAOS $METABIGDATA ; \
		# stack create pallet name=Rocks+HPC \
			# version=$HPCVERSION-$RELEASE \
			# $METABASE $METAOS $METAHPC ; \
		# stack create pallet name=StackIQEnterpriseCloud \
			# version=$CLOUDVERSION-$RELEASE \
			# $METABASE $METAOS $METACLOUD; \
	)
}

tag() {
	for i in $ROLLS
	do
		ROLLNAME=`echo $i | awk -F"," '{ print $1 }'`
		ROLLVER=`echo $i | awk -F"," '{ print $2 }'`
		(cd $ROLLNAME ;
			echo "To tag the code, execute the following commands:" ;
			echo ;
			echo -e "\tcd $ROLLNAME" ;
		 	echo -e "\tgit flow init" ;
			echo -e "\tgit flow release start $RELEASE-$CODENAME-$ROLLVER" ;
			echo -e "\tgit flow release finish $RELEASE-$CODENAME-$ROLLVER" ;
			echo -e "\tgit push" ;
			echo -e "\tgit push --tags" ;
			echo ;
			echo "Use the following text for the commit message:" ;
			echo ;
			list ;
			echo ;
			echo "---------------------------------" ;
			echo ;
		)
	done
}

list() {
	for i in $ROLLS
	do
		ROLLNAME=`echo $i | awk -F"," '{ print $1 }'`
		ROLLVER=`echo $i | awk -F"," '{ print $2 }'`
		echo $ROLLNAME v$ROLLVER
	done
}

status() {
	for i in $ROLLS
	do
		ROLLNAME=`echo $i | awk -F"," '{ print $1 }'`
		ROLLVER=`echo $i | awk -F"," '{ print $2 }'`
		(cd $ROLLNAME ; echo $ROLLNAME ; git status ; echo)
	done
}

pull() {
	for i in $ROLLS
	do
		ROLLNAME=`echo $i | awk -F"," '{ print $1 }'`
		ROLLVER=`echo $i | awk -F"," '{ print $2 }'`
		(cd $ROLLNAME ; echo $ROLLNAME ; git pull ; echo)
	done
}

build() {
	for i in $ROLLS
	do
		ROLLNAME=`echo $i | awk -F"," '{ print $1 }'`
		ROLLVER=`echo $i | awk -F"," '{ print $2 }'`
		(cd $ROLLNAME ; make ROLLVERSION=$ROLLVER RELEASE=$RELEASE roll ;
			stack add pallet clean=y *disk1.iso;
			if [ $ROLLNAME = "roll-os" ]
			then
				stack add pallet *disk2.iso
			fi ;
		)
		(cd $ROLLNAME ; /bin/cp *disk*.iso ../ISOS)
	done
}

nuke() {
	for i in $ROLLS
	do
		ROLLNAME=`echo $i | awk -F"," '{ print $1 }'`
		ROLLVER=`echo $i | awk -F"," '{ print $2 }'`
		(cd $ROLLNAME ; make VERSION=$ROLLVER nuke)
	done
}

check() {
	for i in $ROLLS
	do
		ROLLNAME=`echo $i | awk -F"," '{ print $1 }'`
		ROLLVER=`echo $i | awk -F"," '{ print $2 }'`
		(cd $ROLLNAME ; echo $ROLLNAME ; \
		/opt/stack/share/devel/src/pallet/bin/manifest-check.py ; echo)
	done
}

clone() {
	for i in $ROLLS
	do
		ROLLNAME=`echo $i | awk -F"," '{ print $1 }'`
		ROLLVER=`echo $i | awk -F"," '{ print $2 }'`
		git clone git@git.stacki.com:$ROLLNAME
		(cd $ROLLNAME ; git checkout -b develop origin/develop)
	done
}

usage() {
	echo "Usage: $0 {build | nuke | check | pull | status | clone | meta | list}"
	echo "	build - make RELEASE="$RELEASE "roll"
	echo "	nuke - make nuke"
	echo "	check - manifest-check"
	echo "	pull - git pull"
	echo "	status - git status"
	echo "	clone - git clone"
	echo "	meta - build meta rolls"
	echo "	list - print the rolls that will be operated on"
}

case "$1" in
build)
	pull
	build
	;;

nuke)
	nuke
	;;

check)
	check
	;;

pull)
	pull
	;;

status)
	status
	;;

meta)
	meta
	;;

clone)
	clone
	;;

list)
	list
	;;

tag)
	tag
	;;

*)
	usage
	;;

esac

