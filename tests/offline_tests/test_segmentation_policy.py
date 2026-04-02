from __future__ import annotations

import allure
from assertpy import assert_that

from framework.reporting.allure_helpers import attach_inventory_context, attach_offline_evidence


@allure.parent_suite("Network Security Validation")
@allure.suite("Offline Validation")
@allure.sub_suite("Segmentation Policy")
def test_validate_segmentation_policy_expects_real_batfish_allow_and_deny_results(
    batfish_service,
    lab_topology,
    offline_admin_to_restricted_evaluation,
    offline_user_to_restricted_evaluation,
    offline_validation_result,
) -> None:
    """Validate the two offline segmentation expectations through the Batfish-backed path."""
    attach_inventory_context(lab_topology)
    attach_offline_evidence(offline_validation_result)

    assert_that(
        offline_validation_result["validation"]["passed"],
        description="offline segmentation validation should pass for the current Batfish snapshot",
    ).is_true()
    assert_that(
        offline_validation_result["validation"]["checks"],
        description="offline segmentation validation should produce the two expected policy checks",
    ).is_length(2)
    assert_that(
        offline_validation_result["validation"]["checks"][0]["passed"],
        description="the first offline segmentation check should pass",
    ).is_true()
    assert_that(
        offline_validation_result["validation"]["checks"][1]["passed"],
        description="the second offline segmentation check should pass",
    ).is_true()
    assert_that(
        offline_validation_result["runtime_result"]["backend"],
        description="offline runtime should be fully backed by real Batfish",
    ).is_equal_to("real_batfish")
    assert_that(
        offline_user_to_restricted_evaluation["backend"],
        description="user-to-restricted evaluation should come from the real Batfish backend",
    ).is_equal_to("real_batfish")
    assert_that(
        offline_user_to_restricted_evaluation["action"],
        description="user-to-restricted evaluation should deny traffic",
    ).is_equal_to("deny")
    assert_that(
        offline_admin_to_restricted_evaluation["backend"],
        description="admin-to-restricted evaluation should come from the real Batfish backend",
    ).is_equal_to("real_batfish")
    assert_that(
        offline_admin_to_restricted_evaluation["action"],
        description="admin-to-restricted evaluation should allow traffic",
    ).is_equal_to("allow")
    assert_that(
        offline_validation_result["runtime_result"]["batfish_question_summary"],
        description="offline Batfish evidence should contain one entry per implemented scenario",
    ).is_length(2)
    assert_that(
        batfish_service["network"],
        description="Batfish fixture should point at the configured network name",
    ).is_equal_to("zero_trust_lab")
