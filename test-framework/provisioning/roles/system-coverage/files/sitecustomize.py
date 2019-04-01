import atexit
import os.path

import coverage


if os.path.exists("/etc/SuSE-release"):
	config_file = "/export/test-suites/_common/sles.coveragerc"
else:
	config_file = "/export/test-suites/_common/redhat.coveragerc"

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
