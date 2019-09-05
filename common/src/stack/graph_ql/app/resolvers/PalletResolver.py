# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import graphene
from stack.db import db

class Pallet(graphene.ObjectType):
		id = graphene.Int()
		name = graphene.String()
		version = graphene.String()
		release = graphene.String()
		arch = graphene.String()
		os = graphene.String()
		url = graphene.String()
		# boxes = graphene.Field(lambda: Box)

class Query:
	all_pallets = graphene.List(Pallet)

	def resolve_all_pallets(self, info):
		db.execute("""
		select id, name, version, rel as 'release', arch, os, url
		from rolls
		""")

		return [Pallet(**pallet) for pallet in db.fetchall()]