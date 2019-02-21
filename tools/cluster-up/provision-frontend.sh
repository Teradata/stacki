#!/bin/bash

# Bail on script errors
set -e

# Output the commands as they are run
set -x

# Add the installer ISO for SLES
if [[ $OS == "sles12" ]]
then
    zypper addrepo iso:/?iso=/export/installer-iso/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso os
    zypper update
fi

# Vagrant monkeys with the hosts file, set it back to something known
cat > /etc/hosts <<EOF
127.0.0.1       localhost   localhost.localdomain
$IP     $(echo $FQDN | cut -d '.' -f 1)    $FQDN
EOF

# Set the default gateway through our bridge, if a different one was requested
if [[ -n $GATEWAY ]]
then
    if [[ $OS =~ "sles" ]]
    then
        route del default
        route add default gw $GATEWAY
        sed -i "/DHCLIENT_SET_DEFAULT_ROUTE/d" /etc/sysconfig/network/ifcfg-eth0
    else
        echo "GATEWAY=$GATEWAY" > /etc/sysconfig/network
        echo 'DEFROUTE="no"' >> /etc/sysconfig/network-scripts/ifcfg-eth0
        echo 'PEERDNS="no"' >> /etc/sysconfig/network-scripts/ifcfg-eth0

        systemctl restart network
    fi
fi

# Set the DNS servers, if they were provided
if [[ -n $DNS ]]
then
    sed -i "/nameserver/d" /etc/resolv.conf
    echo "nameserver ${DNS//,/ /}" >> /etc/resolv.conf
fi

# Fetch the barnacle script
curl -sfSLO --retry 3 https://raw.githubusercontent.com/Teradata/stacki/develop/tools/fab/frontend-install.py
chmod u+x frontend-install.py

# Barnacle myself, choosing the second interface
./frontend-install.py --use-existing --stacki-iso="/export/stacki-iso/$ISO_FILENAME" <<< "2"

exit 0
