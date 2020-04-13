#!/bin/bash

# Make sure we have a fresh RPMS folder
rm -rf /export/stack/pallets/Packages-1/15sp1/sles15/sles/x86_64/RPMS
mkdir /export/stack/pallets/Packages-1/15sp1/sles15/sles/x86_64/RPMS
pushd /export/stack/pallets/Packages-1/15sp1/sles15/sles/x86_64/

# Move all RPMS in the pallet to the RPMS folder
find -not -path './RPMS/*' -type f -iname '*.rpm' -exec mv -f {} ./RPMS/ \;

# Make it a repo
createrepo ./

popd 
