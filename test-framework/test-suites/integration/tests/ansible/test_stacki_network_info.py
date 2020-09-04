class TestStackiNetworkInfo:

    def test_no_network_name(self, run_ansible_module):
        result = run_ansible_module("stacki_network_info")

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["networks"]) == 1

    def test_network_name(self, run_ansible_module):
        network_name = "private"
        result = run_ansible_module("stacki_network_info", name=network_name)

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["networks"]) == 1
        assert result.data["networks"][0]["network"] == network_name

    def test_invalid_network_name(self, run_ansible_module):
        network_name = "fake_network_name"
        result = run_ansible_module("stacki_network_info", name=network_name)

        assert "FAIL" in result.status
        assert result.data["changed"] is False

        assert "error" in result.data["msg"]
        assert "not a valid network" in result.data["msg"]