class TestStackiPalletInfo:

    def test_no_pallet_name(self, run_ansible_module):
        result = run_ansible_module("stacki_pallet_info")

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False

    def test_pallet_name(self, run_ansible_module):
        pallet_name = "stacki"
        result = run_ansible_module("stacki_pallet_info", name=pallet_name)

        assert result.status == "SUCCESS"
        assert result.data["changed"] is False
        assert len(result.data["pallets"]) == 1
        assert result.data["pallets"][0]["name"] == pallet_name

    def test_invalid_pallet_name(self, run_ansible_module):
        pallet_name = "fake_pallet_name"
        result = run_ansible_module("stacki_pallet_info", name=pallet_name)

        assert "FAIL" in result.status
        assert result.data["changed"] is False

        assert "error" in result.data["msg"]
        assert "not a valid pallet" in result.data["msg"]