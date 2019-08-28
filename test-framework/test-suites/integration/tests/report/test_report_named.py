import pathlib
import json
import ipaddress

class TestReportNamed:
	def test_on_fresh_install(self, host, revert_etc):
		og_namedconf = pathlib.Path('/etc/named.conf').read_text()

		result = host.run('stack report named | stack report script | bash')
		assert result.rc == 0
		rewritten_namedconf = pathlib.Path('/etc/named.conf').read_text()

		assert rewritten_namedconf == og_namedconf

	def test_with_local_site_add(self, host, revert_etc):
		og_namedconf = pathlib.Path('/etc/named.conf').read_text()
		garbage_string = '# mo stuff'

		pathlib.Path('/etc/named.conf.local').write_text(garbage_string)
		result = host.run('stack report named | stack report script | bash')
		assert result.rc == 0

		rewritten_namedconf = pathlib.Path('/etc/named.conf').read_text()

		assert rewritten_namedconf != og_namedconf
		rewritten_namedconf = rewritten_namedconf.strip().rstrip('include "/etc/rndc.key";')
		assert rewritten_namedconf.strip().endswith(garbage_string)

	def test_with_added_network(self, host, revert_etc, add_network):
		og_namedconf = pathlib.Path('/etc/named.conf').read_text()

		result = host.run('stack list network output-format=json')
		assert result.rc == 0
		assert result.stdout != ''
		nets = json.loads(result.stdout)
		assert len(nets) == 2
		test_net = [net for net in nets if net['network'] != 'private'].pop()

		# add_network fixture doesn't set dns=True, so report named won't have it
		result = host.run(f'stack set network dns {test_net["network"]} dns=True')
		assert result.rc == 0
		# it also creates a network in the same subnet as our 'private', which makes the output weird
		# I don't want to test for that weirdness right now, as it could change.
		result = host.run(f'stack set network address {test_net["network"]} address=10.1.1.0')
		assert result.rc == 0

		result = host.run('stack report named | stack report script | bash')
		assert result.rc == 0

		rewritten_namedconf = pathlib.Path('/etc/named.conf').read_text()
		assert rewritten_namedconf != og_namedconf

		# by default, private is not dns=True
		result = host.run('stack list network dns=true output-format=json')
		assert result.rc == 0
		assert result.stdout != ''
		nets = json.loads(result.stdout)
		assert len(nets) == 1
		test_net = [net for net in nets if net['network'] != 'private'].pop()

		acl_line = '\t127.0.0.0/24;'
		for net in nets:
			# get shorthand notation of network addresses
			acl_line += str(ipaddress.IPv4Interface(f'{net["address"]}/{net["mask"]}')) + ';'
		assert acl_line in rewritten_namedconf

		# check that the reverse zone got added
		# the following jibberish is 'a.b.c.d' -> 'c.b.a.in-addr.arpa'
		rev_zone_addr = '.'.join(test_net['address'].split('.')[2::-1]) + '.in-addr.arpa'
		assert f'zone "{rev_zone_addr}"' in rewritten_namedconf
		assert f'\tfile "reverse.{test_net["network"]}.domain";' in rewritten_namedconf
