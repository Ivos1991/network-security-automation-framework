# Security Scenarios

## Objective

The framework should focus on realistic but portfolio-safe network security scenarios for a zero-trust lab.

## Scenario Categories

### Management-Plane Hardening

Examples:

- SSH enabled while Telnet is disabled
- management access limited to the management segment
- secure AAA or local auth posture present
- insecure legacy services absent

### Segmentation / Reachability

Examples:

- user zone cannot reach restricted service zone directly
- management zone can reach device management interfaces
- approved service-to-service paths are allowed
- forbidden east-west movement is blocked

### Routing / Security Policy

Examples:

- expected routes exist for approved paths
- route leaks between zones are absent
- default route behavior matches lab design
- policy-controlled next-hop intent is preserved

### Drift / Compliance

Examples:

- live device management settings match intended baseline
- observed interfaces map to the intended segmentation model
- deployed config differs from snapshot in a policy-relevant way
- compliance summary shows pass/fail by control family

## First Slice Candidate

Use a narrow scenario set:

- live hardening: verify a lab router or switch is SSH-only on the management plane
- offline segmentation: verify user segment cannot reach restricted service segment in the intended snapshot
- reporting: attach concise Allure evidence for both validations

## Selection Principles

- prefer read-only checks first
- choose scenarios with unambiguous expected outcomes
- use the same device and zone names across live and offline artifacts
- build toward later drift/compliance correlation
