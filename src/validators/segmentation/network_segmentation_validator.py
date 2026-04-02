from __future__ import annotations

from typing import Any


def validate_segmentation_policy(reachability_result: dict[str, Any]) -> dict[str, Any]:
    """Validate each offline reachability result against its expected segmentation action."""
    evaluations = reachability_result.get("evaluations", [])
    checks = []
    for evaluation in evaluations:
        check_passed = evaluation["expected_action"] == evaluation["action"]
        checks.append(
            {
                "source": evaluation["source"],
                "destination": evaluation["destination"],
                "expected_action": evaluation["expected_action"],
                "actual_action": evaluation["action"],
                "passed": check_passed,
            }
        )
    passed = all(check["passed"] for check in checks) if checks else False
    return {
        "passed": passed,
        "checks": checks,
        "summary": "All segmentation expectations matched the intended policy." if passed else "Segmentation expectation failed.",
    }
