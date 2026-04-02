# Live Vs Offline Validation

## Objective

The framework should support two complementary validation paths that answer different questions about the same lab.

## Live Validation

Live validation answers:

- what is running on the devices now
- whether management-plane controls are actually enabled
- whether observed device state matches expected posture

Primary characteristics:

- uses Nornir and Scrapli
- depends on reachable lab devices
- validates observed state
- produces operational evidence from commands and parsed facts

## Offline Validation

Offline validation answers:

- what the intended configs and topology allow or deny
- whether policy design enforces segmentation and routing expectations
- whether a change should pass before touching live infrastructure

Primary characteristics:

- uses PyBatfish
- depends on snapshots and intended topology artifacts
- validates intended state
- produces policy and reachability evidence without live access

## Why Both Are Needed

Neither path is sufficient alone.

Offline-only validation can prove design intent, but it cannot prove the devices are currently hardened or correctly deployed.

Live-only validation can prove observed state, but it cannot reason as cleanly about intended path constraints, pre-change policy, or broad route/policy questions across a snapshot.

## Hybrid Model

The repository should support a hybrid execution story:

1. define intended policy and topology offline
2. validate expected segmentation and routing offline
3. query live devices for observed hardening and key runtime facts
4. compare intended and observed state where appropriate

## Shared Contract

Both paths should feed normalized evidence into common validators or comparison logic where practical. That keeps the design modular and makes drift/compliance checks possible later.

## Practical First Slice

For the first implementation slice:

- live path proves one management-plane hardening control on a running device
- offline path proves one forbidden segmentation path in the intended lab
- integration coverage later ties the two together through shared topology identifiers and policy expectations
