from __future__ import annotations

import allure

from framework.reporting.allure_helpers import attach_inventory_context, attach_live_evidence
from tests.support.assertions import expect_that


@allure.parent_suite("Network Security Validation")
@allure.suite("Live Validation")
@allure.sub_suite("Device Hardening")
def test_device_hardening(lab_topology, live_validation_result) -> None:
    """Validate the mocked live hardening slice and attach compact evidence."""
    attach_inventory_context(lab_topology)
    attach_live_evidence(live_validation_result)

    expect_that(
        live_validation_result["validation"]["ssh_present"],
        "live validation should confirm SSH is enabled",
    ).is_true()
    expect_that(
        live_validation_result["validation"]["telnet_present"],
        "live validation should confirm Telnet is disabled",
    ).is_false()
    expect_that(
        live_validation_result["validation"]["banner_present"],
        "live validation should confirm a login banner is configured",
    ).is_true()
    expect_that(
        live_validation_result["validation"]["passed"],
        "live hardening validation should pass for the default mocked running config",
    ).is_true()
