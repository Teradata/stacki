import pytest

def test_rpms_are_clean(host):
	if host.file('/opt/stack/bin/stack').is_symlink:
		# if we're in use-the-src, we're ok with rpm's being invalid
		pytest.skip("it looks like we're on a devel frontend, skipping package test")

	result = host.run("rpm -qa --qf '%{VENDOR} %{NAME}\n'")
	stacki_pkgs = [pkg.split()[1] for pkg in result.stdout.splitlines() if pkg.startswith('StackIQ')]

	unverified = {}
	for pkg in stacki_pkgs:
		result = host.run(f'rpm -V {pkg}')
		if result.exit_status != 0:
			unverified[pkg] = result

	for pkg, results in unverified.items():
		print(f'{pkg}:\n{results.stdout}')

	assert unverified == {}

def test_no_duplicate_rpms(host):
	result = host.run("rpm -qa | sort | uniq -d")
	assert result.stdout == ''
	assert result.exit_status == 0
