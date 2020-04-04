#!/bin/bash

for i in {1..60}
do
    if grep $1 /var/log/checklist.log | grep -q 'TFTP_RRQ'
    then
        echo "TFTP found for $1"
        break
    fi

    sleep 10
done
