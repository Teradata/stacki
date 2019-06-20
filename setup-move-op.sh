#! /bin/bash
set -x
build=""
declare -a nodes
while true
do
	case "$1" in
		-b|--build) build="true"; shift;;
		-n|--node) nodes+=("$2"); shift 2;;
		--) shift; break;;
		*) break;;
	esac
done

if !(( ${#nodes[@]} ))
	then
		echo "at least one -n or --node is required"
		exit 1
fi

# Build the stacki initrd and squashfs if the build flag is passed.
if [ $build ]
	then
		pushd /export/src/stacki/sles/src/stack/images/
		make clean && make nuke && make
		popd
fi

# Collect built files
mkdir -p /export/move-op/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/sles-stacki.img /export/move-op/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/sles-stacki.img /export/stack/pallets/SLES/12/sp3/sles/x86_64/boot/x86_64/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/stacki-initrd.img /export/move-op/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/SLES-pallet-patches/content /export/move-op/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/SLES-pallet-patches/content /export/stack/pallets/SLES/12/sp3/sles/x86_64/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/SLES-pallet-patches/boot/x86_64/config /export/move-op/
cp /export/src/stacki/build-stacki-nomerge_move_op_shenanigans/BUILD/stack-sles-images-05.02.06.09/SLES/12/sp3/SLES-pallet-patches/boot/x86_64/config /export/stack/pallets/SLES/12/sp3/sles/x86_64/boot/x86_64/
# Switch to the move-op partition scheme
/opt/stack/bin/stack load storage partition file=/export/csv/td-part-sles11-be2.csv

# Setup move op for each node.
/opt/stack/bin/stack set host bootaction "${nodes[@]}" action=console type=install
/opt/stack/bin/stack set host box "${nodes[@]}" box=sles12
/opt/stack/bin/stack set host boot "${nodes[@]}" action=install nukedisks=true nukecontroller=true
for node in "${nodes[@]}"
	do
		ssh "$node" "mkdir -p /var/opt/teradata/move-op/"
		scp /export/move-op/* $node:/var/opt/teradata/move-op/
		ssh "$node" "rpm -i /var/opt/teradata/move-op/teradata-osmigration-11.00.00.07-1.x86_64.rpm"
		ssh "$node" "cp /var/opt/teradata/move-op/osmigration /opt/teradata/osmigration/"
done
