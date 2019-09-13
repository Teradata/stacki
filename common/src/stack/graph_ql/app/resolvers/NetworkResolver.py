# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import ipaddress
from ariadne import ObjectType, QueryType, MutationType
import app.db as db
from app.utils import map_kwargs


query = QueryType()
mutation = MutationType()

@query.field("networks")
@map_kwargs({"id": "id_"})
def resolve_networks(_, info, id_=None, name=None):
    args = []
    params = []
    if id_:
        params.append(" AND id = %s ")
        args.append(id_)
    if name:
        params.append(" AND name = %s ")
        args.append(name)
    cmd = f"SELECT id, name, address, mask, gateway, mtu, zone, dns, pxe FROM subnets  WHERE 1 = 1 {''.join(params)}"
    results, _ = db.run_sql(cmd, args)
    return results

@mutation.field("addNetwork")
def resolve_add_network(obj, info, name, address, mask, gateway=None, zone="", mtu=None, dns=False, pxe=False):

    if name in [network["name"] for network in resolve_networks(obj, info)]:
        raise Exception(f"network {name} exists")

    #validate ip-address
    try:
        ipaddress.IPv4Network(f'{address}/{mask}')
    except:
        msg = '%s/%s is not a valid network address and subnet mask combination'
        raise Exception(msg % (address, mask))

    # Insert network
    cmd = "INSERT INTO subnets (name, address, mask, gateway, zone, mtu, dns, pxe) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    args = (name, address, mask, gateway, zone, mtu, dns, pxe)
    results, _ = db.run_sql(cmd, args)

    # Get the recently inserted value
    results = resolve_networks(obj, info, name=name)
    if results:
        return results[0]
    return None

@mutation.field("updateNetwork")
@map_kwargs({"id": "id_"})
def resolve_update_network(obj, info, id_, name=None, address=None, mask=None, gateway=None, zone=None, mtu=None, dns=None, pxe=None):

    network = resolve_networks(obj, info, id_=id_)

    if not network:
        raise Exception(f"network with {id_} doesn't exist")

    if name:
        if resolve_networks(obj, info, name=name):
            raise Exception(f"network with name {name} already exists")

    if address or mask:
        address1 = address if address else network[0]["address"]
        mask1 = mask if mask else network[0]["mask"]
        #validate address and mask
        try:
            ipaddress.IPv4Network(f'{address1}/{mask1}')
        except:
            msg = '%s/%s is not a valid network address and subnet mask combination'
            raise Exception(msg % (address1, mask1))

    params = []
    args = []

    if name:
        params.append("name=%s")
        args.append(name)
    if address:
        params.append("address=%s")
        args.append(address)
    if mask:
        params.append("mask=%s")
        args.append(mask)
    if gateway:
        params.append("gateway=%s")
        args.append(gateway)
    if zone:
        params.append("zone=%s")
        args.append(zone)
    if mtu:
        params.append("mtu=%s")
        args.append(mtu)
    if dns:
        params.append("dns=%s")
        args.append(dns)
    if pxe:
        params.append("pxe=%s")
        args.append(pxe)

    args.append(id_)

    # Update network
    cmd = f"UPDATE subnets SET {', '.join(params)} WHERE id = %s"
    results, _ = db.run_sql(cmd, args)

    # Get the recently updated value
    results = resolve_networks(obj, info, id_)
    if results:
        return results[0]
    return None

@mutation.field("deleteNetwork")
@map_kwargs({"id": "id_"})
def resolve_delete_network(_, info, id_):

    cmd = "DELETE FROM subnets WHERE id=%s"
    args = (id_,)
    _, affected_rows = db.run_sql(cmd, args)

    if not affected_rows:
        return False

    return True


object_types = []
