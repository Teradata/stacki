#! /bin/sh

for f in $@; do
    unexpand $f > $f-tab
    cp $f $f-orig
    mv $f-tab $f
done

