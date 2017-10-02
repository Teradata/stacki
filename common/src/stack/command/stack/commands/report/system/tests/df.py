import shutil

def test_slash_not_full(host):
	total, used, free = shutil.disk_usage('/')
	assert free > 0

def test_export_not_full(host):
	total, used, free = shutil.disk_usage('/export')
	assert free > 0

def test_var_not_full(host):
	total, used, free = shutil.disk_usage('/var')
	assert free > 0
