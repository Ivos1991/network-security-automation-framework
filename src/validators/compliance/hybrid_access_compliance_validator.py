from __future__ import annotations
def validate_hybrid_access_compliance(
    intended_policy: dict[str, str],
    offline_evaluation: dict[str, object],
    live_signal: dict[str, bool],
) -> dict[str, object]:
    """Check whether intended policy, offline result, and live posture stay aligned."""
    offline_policy_matches = (
        offline_evaluation["source"] == intended_policy["source"]
        and offline_evaluation["destination"] == intended_policy["destination"]
        and offline_evaluation["action"] == intended_policy["action"]
    )
    live_management_ready = live_signal["ssh_enabled"] and not live_signal["telnet_enabled"]
    passed = offline_policy_matches and live_management_ready
    mismatch_reason = ""

    if not offline_policy_matches:
        mismatch_reason = (
            f"Intended {intended_policy['source']} -> {intended_policy['destination']} "
            f"to be {intended_policy['action']}, but offline evaluation returned "
            f"{offline_evaluation['action']}."
        )
    elif not live_management_ready:
        if live_signal["telnet_enabled"]:
            mismatch_reason = (
                "Live management-plane posture is insecure because telnet is enabled."
            )
        elif not live_signal["ssh_enabled"]:
            mismatch_reason = (
                "Live management-plane posture is insecure because ssh is not enabled."
            )
        else:
            mismatch_reason = "Live management-plane posture is not ready for secure administrative access."

    return {
        "passed": passed,
        "offline_policy_matches": offline_policy_matches,
        "live_management_ready": live_management_ready,
        "mismatch_reason": mismatch_reason,
        "summary": (
            "Intended access policy, offline result, and live management posture are aligned."
            if passed
            else "Hybrid drift/compliance correlation failed."
        ),
    }
