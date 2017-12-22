#! /bin/bash
#
# @copyright@
# @copyright@

STACK=/opt/stack/bin/stack

cd /tmp
$STACK report siteattr > site.attrs
$STACK list node xml server attrs=site.attrs > profile.xml
cat profile.xml | $STACK list host profile chapter=main profile=bash > profile.sh 2>&1
bash profile.sh > barnacle.log 2>&1

# TODO - fix add pallet to re-add stuff already on disk
#/opt/stack/bin/stack add pallet $STACKI_URL
#/opt/stack/bin/stack add pallet $OS_URL
#/opt/stack/bin/stack enable pallet %

