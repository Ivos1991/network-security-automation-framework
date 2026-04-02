from __future__ import annotations
import allure
from assertpy import assert_that
from framework.reporting.allure_helpers import attach_inventory_context, attach_live_evidence


@allure.parent_suite("Network Security Validation")
@allure.suite("Live Validation")
@allure.sub_suite("Device Hardening")
def test_validate_device_hardening_expects_secure_management_posture(
    lab_topology,
    live_validation_result,
) -> None:
    """Validate the mocked live hardening slice and attach compact evidence."""
    attach_inventory_context(lab_topology)
    attach_live_evidence(live_validation_result)
    assert_that(live_validation_result["validation"]["ssh_present"],
                description="live validation should confirm SSH is enabled").is_true()
    assert_that(live_validation_result["validation"]["telnet_present"],
                description="live validation should confirm Telnet is disabled").is_false()
    assert_that(live_validation_result["validation"]["banner_present"],
                description="live validation should confirm a login banner is configured").is_true()
    assert_that(live_validation_result["validation"]["passed"],
                description="live hardening validation should pass for the default mocked running config").is_true()
