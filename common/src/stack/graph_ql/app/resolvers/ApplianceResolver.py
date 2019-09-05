# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import graphene
from stack.db import db

class Appliance(graphene.ObjectType):
	id = graphene.Int()
	name = graphene.String()
	public = graphene.String()

class Query(graphene.ObjectType):
	all_appliances = graphene.List(Appliance)
	get_appliance = graphene.Field(Appliance, name=graphene.String(required=True))

	def resolve_all_appliances(self, info):
		db.execute("""
		select id, name, public
		from appliances
		""")

		return [Appliance(**appliance) for appliance in db.fetchall()]

	def resolve_get_appliance(self, info, name):
		db.execute(f'select id, name, public from appliances where name="{name}"')
		
		result = db.fetchall()
		if not result:
			raise Exception(f'appliance "{name}" is not in the database')
		
		return Appliance(**result.pop())