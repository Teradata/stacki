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

# Fetch the barnacle script, if needed
if [[ -f /vagrant/frontend-install.py ]]
then
    mv /vagrant/frontend-install.py .
else
    curl -sfSLO --retry 3 https://raw.githubusercontent.com/Teradata/stacki/$(echo $ISO_FILENAME | cut -d '-' -f -2 | cut -d '_' -f 1)/tools/fab/frontend-install.py
fi

if [[ -f /vagrant/frontend-install.sh ]]
then
    mv /vagrant/frontend-install.sh .
else
    curl -sfSLO --retry 3 https://raw.githubusercontent.com/Teradata/stacki/$(echo $ISO_FILENAME | cut -d '-' -f -2 | cut -d '_' -f 1)/tools/fab/frontend-install.sh
fi

# Barnacle myself, choosing the second interface
chmod u+x frontend-install.py
chmod u+x frontend-install.sh
./frontend-install.sh --use-existing --stacki-iso="/export/stacki-iso/$ISO_FILENAME" <<< "2"

# Allow port forwards to talk on eth0
if [[ -n $FORWARD_PORTS ]]
then
    # Add the vagrant network to Stacki
    /opt/stack/bin/stack add network vagrant zone= $(route -n | grep eth0 | tail -n 1 | awk '{print "address=" $1 " mask=" $3}')

    # Add in the eth0 interface but tell Stacki not to manage it
    /opt/stack/bin/stack add host interface localhost interface=eth0 network=vagrant options=noreport

    # Open up the ports for each forward
    for PAIR in ${FORWARD_PORTS//,/ }
    do
        /opt/stack/bin/stack add firewall network=vagrant service=${PAIR#*:} protocol=all action=ACCEPT chain=INPUT
    done

    # Apply the new firewall rules
    /opt/stack/bin/stack sync host firewall localhost
fi

exit 0
