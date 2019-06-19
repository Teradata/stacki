#! /bin/bash
set -x
build=""
node=""
while true
do
	case "$1" in
		-b|--build) build="true"; shift;;
		-n|--node) node="$2"; shift 2;;
		--) shift; break;;
		*) break;;
	esac
done

if [ -z $node ]; then
	echo "-n or --node is required"
	exit 1
fi

if [ $build ]; then
	pushd /export/src/stacki/sles/src/stack/images/
	make clean && make nuke && make
	popd
fi

ssh $node "mkdir -p /var/opt/teradata/move-op/"
mkdir -p /export/move-op/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/sles-stacki.img /export/move-op/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/sles-stacki.img /export/stack/pallets/SLES/12/sp3/sles/x86_64/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/stacki-initrd.img /export/move-op/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/SLES-pallet-patches/content /export/move-op/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/SLES-pallet-patches/content /export/stack/pallets/SLES/12/sp3/sles/x86_64/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/SLES-pallet-patches/boot/x86_64/config /export/move-op/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/SLES-pallet-patches/boot/x86_64/config /export/stack/pallets/SLES/12/sp3/sles/x86_64/boot/x86_64/
scp /export/move-op/* $node:/var/opt/teradata/move-op/
ssh $node "rpm -i /var/opt/teradata/move-op/teradata-osmigration-11.00.00.07-1.x86_64.rpm"
ssh $node "cp /var/opt/teradata/move-op/osmigration /opt/teradata/osmigration/"
