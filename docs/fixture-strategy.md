# Fixture Strategy

## Objective

Fixtures must keep lab setup explicit, separate shared infrastructure from scenario data, and make the live/offline split easy to understand.

## Root `conftest.py`

Own only broad infrastructure fixtures:

- `config`
- active execution profile
- Allure/reporting hooks
- session logging
- reusable path resolution for lab artifacts

## Local Fixture Ownership

### Live Tests

Keep fixtures near the tests that use them:

- live inventory subset
- device role selection
- command expectations
- optional readiness or connectivity checks

### Offline Tests

Keep intended-state fixtures local:

- Batfish snapshot path
- intended topology model
- segmentation policy fixtures
- expected routes or forbidden paths

### Integration Tests

Own correlation fixtures that pair intended and observed evidence:

- expected management-plane policy
- live device sample set
- intended zones and live interfaces mapping

## Scope Rules

- default to function scope
- use session scope only for expensive setup that is truly shared
- the fixture that establishes mutable lab state owns cleanup
- avoid hidden chains where one fixture silently depends on several others

## Reproducibility Guidance

The first implementation slice should avoid destructive or mutable workflows. Prefer read-only validations so the lab can be rerun consistently.

## Fixture Naming Direction

Use names that reveal security intent rather than tool mechanics:

- `management_plane_targets`
- `intended_segmentation_policy`
- `zero_trust_lab_snapshot`
- `ssh_only_hardening_request`

Avoid vague names like:

- `data`
- `payload`
- `devices`

unless the narrower scope makes the meaning unambiguous.
