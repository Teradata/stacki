import pytest


@pytest.mark.parametrize("command", ["box", "pallet", "cart", "network", "host", "host interface"])
def test_stack_list(command, host, report_output):
	result = host.run(f"stack list {command}")
	assert result.rc == 0
	report_output(f"list {command}", result.stdout)
