import json
from textwrap import dedent


class TestRemoveCart:
	def test_no_args(self, host):
		result = host.run('stack remove cart')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "cart" argument is required
			{cart ...}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove cart test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid cart
			{cart ...}
		''')

	def test_single_arg(self, host, add_cart, revert_etc):
		# Confirm the test cart is there
		result = host.run('stack list cart test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'test',
				'boxes': ''
			}
		]

		# And it has a cart directory
		assert host.file('/export/stack/carts/test').is_directory

		# Now remove it
		result = host.run('stack remove cart test')
		assert result.rc == 0

		# And confirm it is gone
		result = host.run('stack list cart test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid cart
			[cart ...] {expanded=string}
		''')

		# Files should be gone too
		assert not host.file('/export/stack/carts/test').exists

	def test_multiple_args(self, host, add_cart, revert_etc):
		# Create a second cart
		add_cart('foo')

		# Confirm both carts are there
		result = host.run('stack list cart test foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'test',
				'boxes': ''
			},
			{
				'name': 'foo',
				'boxes': ''
			}
		]

		# Now remove our carts
		result = host.run('stack remove cart test foo')
		assert result.rc == 0

		# And confirm they are gone
		result = host.run('stack list cart test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid cart
			[cart ...] {expanded=string}
		''')

		result = host.run('stack list cart foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "foo" argument is not a valid cart
			[cart ...] {expanded=string}
		''')

		# Files should be gone too
		assert not host.file('/export/stack/carts/test').exists
		assert not host.file('/export/stack/carts/foo').exists
