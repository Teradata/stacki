# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import graphene
from promise import Promise
from promise.dataloader import DataLoader
from stack.db import db
from collections import namedtuple
from .InterfaceResolver import Interface

def resolve_interface_with_id(parent, info):
	db.execute(
			f"""
			select i.id as id, n.name as host, mac, ip, netmask, i.gateway,
			i.name as name, device, s.name as subnet, module, vlanid, options, channel, main
			from networks i, nodes n, subnets s
			where i.node = {parent.id} and i.subnet = s.id
			"""
		)

	return [Interface(**interface) for interface in db.fetchall()]

def resolve_appliance_by_name(parent, info, args):
	db.execute(f'select id, name, public from appliances where name="{args["appliance"]}"')
	try:
		return db.fetchall().pop()
	except:
		raise Exception(f'appliance "{args["appliance"]}" is not in the database')

def resolve_box_by_name(parent, info, args):
	db.execute(f'select id, os from boxes where name="{args["box"]}"')
	try:
		return db.fetchall().pop()
	except:
		raise Exception(f'box "{args["box"]}" is not in the database')

def resolve_host_by_name(parent, info, args):
	db.execute(f'select id, name, appliance, box, environment, rack, rank, osaction, installaction, comment, metadata from nodes where name="{args["host"]}"')
	try:
		return db.fetchall().pop()
	except:
		raise Exception(f'box "{args["box"]}" is not in the database')

class Host(graphene.ObjectType):
	id = graphene.Int()
	name = graphene.String()
	rack = graphene.String()
	rank = graphene.String()
	appliance = graphene.String()
	os = graphene.String()
	box = graphene.String()
	environment = graphene.String()
	osaction = graphene.String()
	installaction = graphene.String()
	comment = graphene.String()
	metadata = graphene.String()
	interfaces = graphene.List(lambda: Interface, resolver=resolve_interface_with_id)

class Query:
	all_hosts = graphene.List(Host)
 
	def resolve_all_hosts(self, info, **kwargs):
		db.execute(
			"""
			select n.id as id, n.name as name, n.rack as rack, n.rank as rank,
			n.comment as comment, n.metadata as metadata,	a.name as appliance,
			o.name as os, b.name as box, e.name as environment,
			bno.name as osaction, bni.name as installaction
			from nodes n
			left join appliances a   on n.appliance     = a.id
			left join boxes b        on n.box           = b.id
			left join environments e on n.environment   = e.id
			left join bootnames bno  on n.osaction      = bno.id
			left join bootnames bni  on n.installaction = bni.id
			left join oses o	 on b.os            = o.id
			"""
		)

		return [Host(**host) for host in db.fetchall()]

class AddHost(graphene.Mutation):
	class Arguments:
		name = graphene.String(required=True)
		appliance = graphene.String(required=True)
		rack = graphene.String(required=True)
		rank = graphene.String(required=True)
		box = graphene.String(default_value='default')
		osaction = graphene.String(default_value='default')
		installaction = graphene.String(default_value='default')
		environment = graphene.String(default_value=False)
	
	ok = graphene.Boolean()

	def mutate(root, info, **kwargs):
		# TODO: Reduce number of queries
		appliance = resolve_appliance_by_name(root, info, kwargs)['id']
		box = resolve_box_by_name(root, info, kwargs)
		

		db.execute(f'select name from nodes where name="{kwargs["name"]}"')
		if db.fetchall():
			raise Exception(f'host "{kwargs["name"]}" already exists in the database')

		db.execute('''
				select bn.id as id from
				bootactions ba, bootnames bn
				where ba.bootname = bn.id
				and ba.os = %s
				and bn.name = "%s"
				and bn.type = "install"
				''' % (box['os'], kwargs['installaction']))
		try:
			install_id = db.fetchall().pop()['id']
		except:
			raise Exception(f'installaction "{kwargs["installaction"]}" does not exist')

		db.execute('''
				select bn.id as id from
				bootactions ba, bootnames bn
				where ba.bootname = bn.id
				and bn.name = "%s"
				and bn.type = "os"
				''' % kwargs['installaction'])
		try:
			os_id = db.fetchall().pop()['id']
		except:
			raise Exception(f'osaction "{kwargs["installaction"]}" does not exist')

		environment = None
		if kwargs['environment']:
			db.execute(f'select id, name from environments where name="{kwargs["name"]}"')
			try:
				environment = db.fetchall().pop()['id']
			except:
				raise Exception(f'environment "{kwargs["environment"]}" is not in the database')

		db.execute('''
			insert into nodes
			(name, rack, rank, installaction, osaction, appliance, box, environment)
			values (%s, %s, %s, %s, %s, %s, %s, %s) 
			''', (
				kwargs['name'],
				kwargs['rack'],
				kwargs['rank'],
				install_id,
				box['os'],
				appliance,
				box['id'],
				environment,
				)
			)
		ok = True
		return AddHost(ok=ok)

class Mutations(graphene.ObjectType):
	add_host = AddHost.Field()