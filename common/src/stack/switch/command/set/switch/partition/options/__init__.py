# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import SwitchArgProcessor
from stack.commands.sync.switch.ib import enforce_subnet_manager
from stack.exception import ArgRequired, ParamValue, CommandError


class Command(SwitchArgProcessor, stack.commands.Command):
	"""
	Sets the infiniband partition flags in the Stacki database.
	Note that a sync is still required to enact this change on the switch.

	<arg type='string' name='switch'>
	The name of the switches on which to set these options.
	</arg>

	<param type='string' name='name' optional='0'>
	The name of the partition to set this flag on.  Must either be 'Default'
	or a hex value between 0x0001-0x7ffe (1 and 32,766).  The name will be
	normalized to the lower-case, leading-zero hex format: 'aaa' -> '0x0aaa'
	</param>

	<param type='string' name='options' optional='1'>
	A list of options to set on the partition.  The format is 
	'flag=value flag2=value2'.  Currently supported are 'ipoib=True|False'
	and 'defmember=limited|full'.  Unless explicitly specified, 'ipoib' and
	'defmember' are not set.
	</param>

	<param type='boolean' name='enforce_sm' optional='1'>
	If a switch is not an infiniband subnet manager an error will be raised.
	</param>

	"""

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'switch')

		name, options_param, enforce_sm, force_add = self.fillParams([
			('name', None, True),
			('options', None),
			('enforce_sm', False),
			('force_add', True),
		])

		# force is really whether or not this command came from ADD vs SET
		stack_set = self.str2bool(force_add)

		name = name.lower()
		if name == 'default':
			name = 'Default'
			pkey = 0x7fff
		else:
			try:
				pkey = int(name, 16)
				name = '0x{0:04x}'.format(pkey)
			except ValueError:
				raise ParamValue(self, 'name', 'a hex value between 0x0001 and 0x7ffe, or "default"')

		parsed_options = []
		if options_param:
			options = options_param.split()
			bad_options = [opt for opt in options if '=' not in opt]
			options = dict(opt.split('=') for opt in options_param.split() if '=' in opt)
			if 'ipoib' in options:
				parsed_options.append(f"ipoib={self.str2bool(options['ipoib'])}")
				del options['ipoib']
			if 'defmember' in options and options['defmember'].lower() in ['limited', 'full']:
				parsed_options.append(f"defmember={options['defmember'].lower()}")
				del options['defmember']
			if options:
				# if there's any leftover, error
				msg = 'The following are invalid partition options: '
				raise CommandError(self, msg + ' '.join(f'{k}={v}' for k, v in options.items()))
			if bad_options:
				# if there's non-key value, error
				msg = 'The following are invalid partition options: '
				raise CommandError(self, msg + ' '.join(bad_options))

		parsed_options_str = ' '.join(parsed_options)

		switches = self.getSwitchNames(args)
		switch_attrs = self.getHostAttrDict(switches)
		for switch in switches:
			if switch_attrs[switch].get('switch_type') != 'infiniband':
				raise CommandError(self, f'{switch} does not have a switch_type of "infiniband"')

		if self.str2bool(enforce_sm):
			enforce_subnet_manager(self, switches)

		ids_sql = 'name, id FROM nodes WHERE name IN (%s)' % ','.join(['%s'] * len(switches))
		sw_ids = dict((row[0], row[1]) for row in self.db.select(ids_sql, tuple(switches)))

		sql_check = 'id, options FROM ib_partitions WHERE switch=%s AND part_name=%s'
		for switch in switches:
			# if doing an ADD, we want to ensure the partition doesn't already exist
			exists = self.db.select(sql_check, (sw_ids[switch], name))
			# since there's already a switch dict, use that to store some temporary data
			switch_attrs[switch]['_part_opts'] = parsed_options_str
			if not exists:
				continue

			# since there's already a switch dict, use that to store some temporary data
			switch_attrs[switch]['_part_id'] = exists[0][0]

			if not stack_set:
				raise CommandError(self, f'partition "{name}" already exists on switch "{switch}"')
			if options_param is None:
				# if user supplied no options field, for existing keep the previous options field
				switch_attrs[switch]['_part_opts'] = exists[0][1]

		# if it already exists, we do an UPDATE instead
		sql_update = 'UPDATE ib_partitions SET switch=%s, part_key=%s, part_name=%s, options=%s WHERE switch=%s and id=%s'
		sql_insert = 'INSERT INTO ib_partitions (switch, part_key, part_name, options) VALUES (%s, %s, %s, %s)'

		for switch in switches:
			if stack_set and exists:
				self.db.execute(sql_update, (sw_ids[switch], pkey, name, switch_attrs[switch]['_part_opts'], sw_ids[switch], switch_attrs[switch]['_part_id']))
			else:
				self.db.execute(sql_insert, (sw_ids[switch], pkey, name, switch_attrs[switch]['_part_opts']))
