from __future__ import annotations
def validate_device_hardening(running_config: str) -> dict[str, object]:
    """Validate the current hardening expectations against a running config string."""
    normalized_config = running_config.lower()
    ssh_present = "ssh" in normalized_config
    telnet_present = "telnet" in normalized_config
    banner_present = "banner login" in normalized_config
    passed = ssh_present and not telnet_present and banner_present

    return {
        "passed": passed,
        "ssh_present": ssh_present,
        "telnet_present": telnet_present,
        "banner_present": banner_present,
        "summary": (
            "SSH is present, Telnet is absent, and a login banner is configured."
            if passed
            else "Hardening expectation failed."
        ),
    }
