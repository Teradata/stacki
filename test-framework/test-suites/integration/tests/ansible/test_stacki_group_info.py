class TestStackiGroupInfo:
    def test_no_group_or_host_name(self, host,add_host, add_group, run_ansible_module):
        add_host("backend-0-1", "0", "1", "backend")
        add_group("test2")

        result = host.run("stack add host group backend-0-0 group=test")

        assert result.rc == 0

        result = host.run("stack add host group backend-0-1 group=test2")

        assert result.rc == 0

        result = run_ansible_module("stacki_group_info")

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["hostgroups"]) == 2

    def test_single_group(self, host, add_group, run_ansible_module):
        result = host.run("stack add host group backend-0-0 group=test")

        assert result.rc == 0

        result = run_ansible_module("stacki_group_info", group=["test"])

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["hostgroups"]) == 1

    def test_multiple_groups(self, host, add_group, run_ansible_module):
        add_group("test2")
        add_group("test3")

        result = host.run("stack add host group backend-0-0 group=test")

        assert result.rc == 0

        result = host.run("stack add host group backend-0-0 group=test2")

        assert result.rc == 0

        result = run_ansible_module("stacki_group_info", group=["test", "test2", "test3"])

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["hostgroups"]) == 2

    def test_single_host(self, host, add_group, run_ansible_module):
        result = host.run("stack add host group backend-0-0 group=test")

        assert result.rc == 0

        result = run_ansible_module("stacki_group_info", host=["backend-0-0"])

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["hostgroups"]) == 1

    def test_multiple_hosts(self, host, add_host, add_group, run_ansible_module):
        add_host("backend-0-1", "0", "1", "backend")

        add_group("test2")

        result = host.run("stack add host group backend-0-0 group=test")

        assert result.rc == 0

        result = host.run("stack add host group backend-0-1 group=test2")

        assert result.rc == 0

        result = run_ansible_module("stacki_group_info", host=["backend-0-0", "backend-0-1"])

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["hostgroups"]) == 2

    def test_invalid_group(self, run_ansible_module):
        result = run_ansible_module("stacki_group_info", group=["fake_group"])

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["hostgroups"]) == 0

    def test_invalid_host(self, run_ansible_module):
        result = run_ansible_module("stacki_group_info", host=["fake_host"])

        assert result.status == "FAILED!"
        assert result.data["changed"] is False
        assert "error" in result.data["msg"]
        assert "cannot resolve host" in result.data["msg"]
