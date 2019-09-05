# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import graphene
from stack.db import db
from collections import namedtuple


class Attribute(graphene.Interface):
	# TODO: The 'type' variable should be renamed
	type = graphene.String()
	scope = graphene.String()
	attr = graphene.String()
	value = graphene.String()

	def resolve_type(self, info):
		if self.type == 1:
			return 'shadow'
		else:
			return 'var'

class GlobalAttribute(graphene.ObjectType):
	class Meta:
		interfaces = (Attribute, )

	shadow = graphene.String()

class HostAttribute(graphene.ObjectType):
	class Meta:
		interfaces = (Attribute, )

	name = graphene.String()
	shadow = graphene.String()

class ApplianceAttribute(graphene.ObjectType):
	"""Attributes with the appliance scope"""
	class Meta:
		interfaces = (Attribute, )

	appliance = graphene.String()

class Query:
	all_attributes = graphene.List(GlobalAttribute)
	host_attributes = graphene.List(HostAttribute)
	appliance_attributes = graphene.List(ApplianceAttribute)

	def resolve_all_attributes(self, info, **kwargs):
		db.execute(
		"""
		select * from attributes
		"""
		)
		attributes = db.fetchall()
		Attribute = namedtuple(
				"Attribute", ["scope", "attr", "value", "shadow", "scope_id"]
		)

		attrs = [Attribute(**attr) for attr in attributes]

		return attrs

	def resolve_host_attributes(self, info, **kwargs):
		db.execute(
		"""
		select false as type, scope, attr, value, name
		from attributes, nodes n
		where scope = 'host' and scopeid = n.id 
		"""
		)

		return [HostAttribute(**attr) for attr in db.fetchall()]

	def resolve_appliance_attributes(self, info, **kwargs):
		db.execute(
		"""
		select false as type, att.scope as scope,
		att.attr as attr, value, app.name as appliance
		from attributes att, appliances app
		where att.scope = 'appliance' and att.scopeid = app.id
		"""
		)

		return [ApplianceAttribute(**attr) for attr in db.fetchall()]