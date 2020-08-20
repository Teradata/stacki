class TestStackiGroupInfo:
    def test_no_groups(self, run_ansible_module):
        result = run_ansible_module("stacki_group_info")

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["groups"]) == 0

    def test_single_groups(self, add_group, run_ansible_module):
        result = run_ansible_module("stacki_group_info")

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["groups"]) == 1

    def test_multiple_groups(self, host, add_group, add_host, run_ansible_module):
        add_group("test2")
        add_host("backend-0-1", "0", "1", "backend")

        result = host.run("stack add host group backend-0-0 group=test")

        assert result.rc == 0

        result = host.run("stack add host group backend-0-1 group=test")

        assert result.rc == 0

        result = host.run("stack add host group backend-0-1 group=test2")

        assert result.rc == 0

        result = run_ansible_module("stacki_group_info")

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["groups"]) == 2

        assert result.data["groups"][0]["group"] == "test"
        assert len(result.data["groups"][0]["hosts"]) == 2

        assert result.data["groups"][1]["group"] == "test2"
        assert len(result.data["groups"][1]["hosts"]) == 1
