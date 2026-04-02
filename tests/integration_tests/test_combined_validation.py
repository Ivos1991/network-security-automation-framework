from __future__ import annotations

import allure
from assertpy import assert_that

from framework.reporting.allure_helpers import (
    attach_compliance_evidence,
    attach_hybrid_aggregation_summary,
    attach_hybrid_evidence,
    attach_inventory_context,
    attach_live_evidence,
    attach_offline_evidence,
    attach_validation_summary,
)


@allure.parent_suite("Network Security Validation")
@allure.suite("Integration Validation")
@allure.sub_suite("Combined Live And Offline")
def test_validate_combined_flow_expects_all_paths_to_pass(
    hybrid_validation_result,
    lab_topology,
    live_validation_result,
    management_plane_compliance_result,
    offline_validation_result,
) -> None:
    """Verify the current happy-path flow across live, offline, and hybrid slices."""
    attach_inventory_context(lab_topology)
    attach_live_evidence(live_validation_result)
    attach_offline_evidence(offline_validation_result)
    attach_compliance_evidence(management_plane_compliance_result)
    attach_hybrid_evidence(hybrid_validation_result)
    attach_validation_summary(
        "integration-validation-summary",
        {
            "live_passed": live_validation_result["validation"]["passed"],
            "offline_passed": offline_validation_result["validation"]["passed"],
            "compliance_passed": management_plane_compliance_result["validation"]["passed"],
            "hybrid_status": hybrid_validation_result["compliance_status"]["overall_status"],
            "hybrid_mismatch_type": hybrid_validation_result["compliance_status"]["mismatch_type"],
            "device": live_validation_result["runtime_result"]["host"],
            "snapshot": offline_validation_result["runtime_result"]["snapshot_name"],
        },
    )

    assert_that(
        live_validation_result["validation"]["passed"],
        description="live validation should pass in the combined integration scenario",
    ).is_true()
    assert_that(
        offline_validation_result["validation"]["passed"],
        description="offline validation should pass in the combined integration scenario",
    ).is_true()
    assert_that(
        management_plane_compliance_result["validation"]["passed"],
        description="management-plane compliance should pass in the combined integration scenario",
    ).is_true()
    assert_that(
        hybrid_validation_result["compliance_status"]["overall_status"],
        description="hybrid happy path should report an overall pass status",
    ).is_equal_to("pass")
    assert_that(
        hybrid_validation_result["compliance_status"]["mismatch_type"],
        description="hybrid happy path should not report a mismatch type",
    ).is_equal_to("none")
    assert_that(
        offline_validation_result["runtime_result"]["backend"],
        description="combined integration scenario should use the real Batfish offline backend",
    ).is_equal_to("real_batfish")
    assert_that(
        offline_validation_result["runtime_result"]["batfish_question_summary"],
        description="combined integration scenario should expose the two Batfish evidence entries",
    ).is_length(2)


@allure.parent_suite("Network Security Validation")
@allure.suite("Integration Validation")
@allure.sub_suite("Hybrid Compliance Negative Case")
def test_validate_hybrid_access_compliance_expects_offline_mismatch_result(
    hybrid_offline_mismatch_result,
    lab_topology,
) -> None:
    """Verify the offline-side hybrid mismatch contract stays normalized and readable."""
    attach_inventory_context(lab_topology)
    attach_hybrid_evidence(hybrid_offline_mismatch_result)
    attach_validation_summary(
        "hybrid-negative-summary",
        {
            "overall_status": hybrid_offline_mismatch_result["compliance_status"]["overall_status"],
            "mismatch_type": hybrid_offline_mismatch_result["compliance_status"]["mismatch_type"],
            "mismatch_reason": hybrid_offline_mismatch_result["compliance_status"]["mismatch_reason"],
            "offline_action": hybrid_offline_mismatch_result["compliance_status"]["offline_result"]["action"],
            "intended_action": hybrid_offline_mismatch_result["compliance_status"]["intended_policy"]["action"],
        },
    )

    assert_that(
        hybrid_offline_mismatch_result["compliance_status"]["overall_status"],
        description="offline-side hybrid mismatch should report a fail status",
    ).is_equal_to("fail")
    assert_that(
        hybrid_offline_mismatch_result["compliance_status"]["mismatch_type"],
        description="offline-side hybrid mismatch should report the offline policy mismatch type",
    ).is_equal_to("offline_policy_mismatch")
    assert_that(
        hybrid_offline_mismatch_result["validation"]["offline_policy_matches"],
        description="offline-side hybrid mismatch should flag the offline policy as misaligned",
    ).is_false()
    assert_that(
        hybrid_offline_mismatch_result["validation"]["live_management_ready"],
        description="offline-side hybrid mismatch should preserve the live management-ready signal",
    ).is_true()
    assert_that(
        hybrid_offline_mismatch_result["compliance_status"]["mismatch_reason"],
        description="offline-side hybrid mismatch reason should explain the deny result",
    ).contains("offline evaluation returned deny")


@allure.parent_suite("Network Security Validation")
@allure.suite("Integration Validation")
@allure.sub_suite("Hybrid Compliance Live Negative Case")
def test_validate_hybrid_access_compliance_expects_live_mismatch_result(
    hybrid_live_mismatch_result,
    lab_topology,
) -> None:
    """Verify the live-side hybrid mismatch contract stays normalized and readable."""
    attach_inventory_context(lab_topology)
    attach_hybrid_evidence(hybrid_live_mismatch_result)
    attach_validation_summary(
        "hybrid-live-negative-summary",
        {
            "overall_status": hybrid_live_mismatch_result["compliance_status"]["overall_status"],
            "mismatch_type": hybrid_live_mismatch_result["compliance_status"]["mismatch_type"],
            "mismatch_reason": hybrid_live_mismatch_result["compliance_status"]["mismatch_reason"],
            "offline_action": hybrid_live_mismatch_result["compliance_status"]["offline_result"]["action"],
            "telnet_enabled": hybrid_live_mismatch_result["compliance_status"]["live_posture_status"]["telnet_enabled"],
        },
    )

    assert_that(
        hybrid_live_mismatch_result["compliance_status"]["overall_status"],
        description="live-side hybrid mismatch should report a fail status",
    ).is_equal_to("fail")
    assert_that(
        hybrid_live_mismatch_result["compliance_status"]["mismatch_type"],
        description="live-side hybrid mismatch should report the live posture mismatch type",
    ).is_equal_to("live_posture_mismatch")
    assert_that(
        hybrid_live_mismatch_result["validation"]["offline_policy_matches"],
        description="live-side hybrid mismatch should preserve the offline policy alignment",
    ).is_true()
    assert_that(
        hybrid_live_mismatch_result["validation"]["live_management_ready"],
        description="live-side hybrid mismatch should flag the live posture as insecure",
    ).is_false()
    assert_that(
        hybrid_live_mismatch_result["compliance_status"]["mismatch_reason"],
        description="live-side hybrid mismatch reason should mention Telnet exposure",
    ).contains("telnet is enabled")


@allure.parent_suite("Network Security Validation")
@allure.suite("Integration Validation")
@allure.sub_suite("Hybrid Compliance Aggregation")
def test_aggregate_hybrid_compliance_statuses_expects_correct_result(
    hybrid_aggregation_result,
) -> None:
    """Verify suite-level hybrid aggregation remains deterministic across current outcomes."""
    aggregation = hybrid_aggregation_result["aggregation"]
    attach_hybrid_aggregation_summary(aggregation.model_dump())

    assert_that(
        aggregation.total_results,
        description="hybrid aggregation should summarize the three current hybrid outcomes",
    ).is_equal_to(3)
    assert_that(
        aggregation.passed_results,
        description="hybrid aggregation should report one passing result",
    ).is_equal_to(1)
    assert_that(
        aggregation.failed_results,
        description="hybrid aggregation should report two failing results",
    ).is_equal_to(2)
    assert_that(
        aggregation.mismatch_type_counts["none"],
        description="hybrid aggregation should count one aligned result",
    ).is_equal_to(1)
    assert_that(
        aggregation.mismatch_type_counts["offline_policy_mismatch"],
        description="hybrid aggregation should count one offline policy mismatch",
    ).is_equal_to(1)
    assert_that(
        aggregation.mismatch_type_counts["live_posture_mismatch"],
        description="hybrid aggregation should count one live posture mismatch",
    ).is_equal_to(1)
    assert_that(
        aggregation.summary,
        description="hybrid aggregation summary should stay deterministic for reporting",
    ).is_equal_to(
        "3 hybrid results: 1 passed, 2 failed; mismatch types: "
        "none=1, offline_policy_mismatch=1, live_posture_mismatch=1"
    )
