# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
# 

import re
import stack.commands
from stack.db import database as db, BaseModel
from pprint import pprint

class command(stack.commands.report.command):
	pass

class Command(command):
	"""
	Output the GraphQL schema definition (SDL) generated with the database schema.
	"""

	def get_table_names(self):
		"""
		Returns a list of the table names in the database
		"""

		return self.model_dict.keys()

	def get_table_description(self, table_name):
		"""
		return list of descriptions
		"""

		return self.model_dict[table_name]._meta.columns


	def get_table_references(self, table_name):
		"""
		return list of references
		"""

		return db.get_foreign_keys(table_name)

	def get_scalar_value(self, string, required = False):
		scalars = {
			'varchar': 'String',
			'text': 'String',
			'int': "Int",
			'enum': 'String', # TODO: Create enum here
		}

		check_string = string.lower()

		for scalar in scalars:
			if scalar in check_string:
				ext = '!' if required else ''
				return f"{scalars[scalar]}{ext}"

	def generate_type_fields(self, table_name, description, reference):
		fields = {}
		for field_name, field in description.items():
			field_name = self.camel_case_it(field.name)
			field_type = self.get_scalar_value(field.field_type, not field.null)
			fields[field_name] = field_type

		for field in reference:
			if not field.dest_table:
				continue
			field_name = self.camel_case_it(field.column)
			field_type = self.pascal_case_it(field.dest_table)
			fields[field_name] = field_type

		return fields

	def generate_type_field_strings(self, field_types):
		"""Returns field types "Id: String" """
		fields = []
		for k, v in field_types.items():
			fields.append("  {}: {}".format(k, v))
		return "\n".join(fields)

	def generate_query_type_field(self, table_name):
		return (self.camel_case_it(table_name), self.pascal_case_it(table_name))

	def generate_query_type_field_strings(self, query_types):
		"""Returns query field types "nodes: [Nodes]" """
		return "  {}: [{}]".format(*query_types)

	def camel_case_it(self, string, delimeter = "_"):
		"""Return string in camelCase form"""
		string = "".join([word.capitalize() for word in string.split(delimeter)])
		return string[0].lower() + string[1:]

	def pascal_case_it(self, string, delimeter = "_"):
		"""Return string in PascalCase form"""
		return "".join([word.capitalize() for word in string.split(delimeter)])

	def generate_types(self):

		gql_types = []
		for table_name in self.get_table_names():
			description = self.get_table_description(table_name)
			reference = self.get_table_references(table_name)
			gql_types.append({
				self.pascal_case_it(table_name): self.generate_type_fields(table_name, description, reference)
			})

		types_list = []
		for gql_type in gql_types:
			for type_name, type_values in gql_type.items():
				types_list.append("type %s {\n%s\n}\n" % (type_name, self.generate_type_field_strings(type_values)))

		return types_list

	def generate_model_dict(self):
		model_dict = {}
		for model in BaseModel.__subclasses__():
			model_dict[model._meta.table_name] = model

		return model_dict

	def generate_queries(self):

		gql_types = []
		for table_name in self.get_table_names():
			gql_types.append(self.generate_query_type_field(table_name))

		query_list = ["extend type Query {",]
		for gql_type in gql_types:
			query_list.append(self.generate_query_type_field_strings(gql_type))

		query_list.append("}")
		return query_list

	def run(self, params, args):

		self.model_dict = self.generate_model_dict()

		self.beginOutput()

		self.addOutput(self, "\n".join(self.generate_types()))
		self.addOutput(self, "\n".join(self.generate_queries()))

		self.endOutput(padChar='', trimOwner=True)