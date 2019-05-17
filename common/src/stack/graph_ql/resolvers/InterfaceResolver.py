# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import graphene
from stack.db import db

class Interface(graphene.ObjectType):
    id = graphene.Int()
    host = graphene.String()
    mac = graphene.String()
    ip = graphene.String()
    netmask = graphene.String()
    gateway = graphene.String()
    name = graphene.String()
    device = graphene.String()
    subnet = graphene.String()
    module = graphene.String()
    vlanid = graphene.Int()
    options = graphene.String()
    channel = graphene.String()
    main = graphene.Int()

class Query:
	all_interfaces = graphene.List(Interface)

	def resolve_all_interfaces(self, info):
		db.execute("""
		select i.id as id, n.name as host, mac, ip, netmask, i.gateway,
		i.name as name, device, s.name as subnet, module, vlanid, options, channel, main
		from networks i, nodes n, subnets s
		where i.node = n.id and i.subnet = s.id
		""")

		return [Interface(**interface) for interface in db.fetchall()]