from __future__ import annotations

import allure

from framework.reporting.allure_helpers import attach_inventory_context, attach_offline_evidence
from tests.support.assertions import expect_that


@allure.parent_suite("Network Security Validation")
@allure.suite("Offline Validation")
@allure.sub_suite("Segmentation Policy")
def test_segmentation_policy(
    batfish_service,
    lab_topology,
    offline_admin_to_restricted_evaluation,
    offline_user_to_restricted_evaluation,
    offline_validation_result,
) -> None:
    """Validate the two offline segmentation expectations through the Batfish-backed path."""
    attach_inventory_context(lab_topology)
    attach_offline_evidence(offline_validation_result)

    expect_that(
        offline_validation_result["validation"]["passed"],
        "offline segmentation validation should pass for the current Batfish snapshot",
    ).is_true()
    expect_that(
        offline_validation_result["validation"]["checks"],
        "offline segmentation validation should produce the two expected policy checks",
    ).is_length(2)
    expect_that(
        offline_validation_result["validation"]["checks"][0]["passed"],
        "the first offline segmentation check should pass",
    ).is_true()
    expect_that(
        offline_validation_result["validation"]["checks"][1]["passed"],
        "the second offline segmentation check should pass",
    ).is_true()
    expect_that(
        offline_validation_result["runtime_result"]["backend"],
        "offline runtime should be fully backed by real Batfish",
    ).is_equal_to("real_batfish")
    expect_that(
        offline_user_to_restricted_evaluation["backend"],
        "user-to-restricted evaluation should come from the real Batfish backend",
    ).is_equal_to("real_batfish")
    expect_that(
        offline_user_to_restricted_evaluation["action"],
        "user-to-restricted evaluation should deny traffic",
    ).is_equal_to("deny")
    expect_that(
        offline_admin_to_restricted_evaluation["backend"],
        "admin-to-restricted evaluation should come from the real Batfish backend",
    ).is_equal_to("real_batfish")
    expect_that(
        offline_admin_to_restricted_evaluation["action"],
        "admin-to-restricted evaluation should allow traffic",
    ).is_equal_to("allow")
    expect_that(
        offline_validation_result["runtime_result"]["batfish_question_summary"],
        "offline Batfish evidence should contain one entry per implemented scenario",
    ).is_length(2)
    expect_that(
        batfish_service["network"],
        "Batfish fixture should point at the configured network name",
    ).is_equal_to("zero_trust_lab")
