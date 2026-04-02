# Topology Strategy

## Objective

The repository needs a small but credible zero-trust lab topology that supports both live and offline validation without becoming operationally heavy.

## First Topology Direction

Start with a compact lab that has:

- one management segment
- one user/application segment
- one restricted service segment
- a small set of routers or L3 devices that enforce policy boundaries

This is enough to demonstrate:

- management-plane hardening checks
- allowed management access
- forbidden east-west reachability
- route and policy intent

## Artifact Types

The topology strategy should support both execution paths through shared identifiers:

- intended node inventory
- intended links
- intended zones
- intended policy matrix
- configuration snapshots for offline analysis
- live inventory for device access

## Normalization Rule

Hostnames, interface names, VRFs, zones, and address objects should use one canonical naming scheme so live and offline results can be correlated later.

## Reproducibility Guidance

The first topology should be:

- small enough to run locally
- stable across repeated executions
- easy to describe in portfolio documentation
- independent from any real enterprise environment

## Future Expansion

Once the first slice is stable, the topology can expand to include:

- additional security zones
- redundant paths
- route redistribution scenarios
- drift-focused config deltas

The repository should not start there. The first value comes from a tiny, reliable lab.
