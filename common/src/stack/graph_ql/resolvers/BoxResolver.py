# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import graphene
from stack.db import db

class Box(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    os = graphene.String()
		# TODO: Pallets
    # pallets = graphene.List(lambda: Pallet)

class Query:
	all_boxes = graphene.List(Box)

	def resolve_all_boxes(self, info):
		db.execute("""
		select b.id as id, b.name as name, o.name as os
		from boxes b, oses o
		where b.os = o.id
		""")

		return [Box(**box) for box in db.fetchall()]