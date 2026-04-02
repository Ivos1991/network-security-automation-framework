from __future__ import annotations
def validate_management_plane_compliance(
    intended_posture: dict[str, bool],
    observed_posture: dict[str, bool],
) -> dict[str, object]:
    """Compare intended and observed management-plane posture field by field."""
    checks = []
    for field in ("ssh_enabled", "telnet_enabled", "banner_login_present"):
        intended_value = intended_posture[field]
        observed_value = observed_posture[field]
        checks.append(
            {
                "field": field,
                "intended": intended_value,
                "observed": observed_value,
                "passed": intended_value == observed_value,
            }
        )

    passed = all(check["passed"] for check in checks)
    return {
        "passed": passed,
        "checks": checks,
        "summary": (
            "Observed management-plane posture matches intended posture."
            if passed
            else "Observed management-plane posture differs from intended posture."
        ),
    }
