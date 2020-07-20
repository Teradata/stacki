import atexit
from pathlib import Path

import coverage


def get_distro():
	''' get the distro on any newer systemd based distro (sles12+, centos/rhel 7+) '''
	os_release = Path('/etc/os-release')
	if not os_release.exists():
		raise NotImplementedError

	for line in os_release.read_text().splitlines():
		if line.startswith('ID='):
			distro_id = line.split('=')[-1].strip('"')
			break
	else: # nobreak
		raise NotImplementedError

	if distro_id in ['rhel', 'centos']:
		return 'redhat'

	return distro_id


config_file = f"/export/test-suites/_common/{get_distro()}.coveragerc"

cov = coverage.Coverage(
	data_file="/root/.coverage",
	data_suffix=True,
	config_file=config_file,
	source=["stack", "wsclient"]
)
cov.start()

@atexit.register
def stop_coverage():
	cov.stop()
	cov.save()
