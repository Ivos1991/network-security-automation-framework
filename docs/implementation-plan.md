# Implementation Plan

## Phase 0: Planning

Deliver the repository planning set before any code:

- current reference analysis
- reusable patterns
- target architecture
- fixture strategy
- reporting and CI
- topology strategy
- live vs offline validation model
- security scenarios
- coding standards

## Phase 1: First Narrow Slice

Build one small zero-trust lab demonstration with:

- a tiny intended topology
- one live management-plane hardening validation
- one offline segmentation validation
- Allure output for both

## Phase 2: Framework Baseline

Introduce the minimum reusable framework modules:

- config manager
- inventory loader
- live execution adapter
- offline execution adapter
- shared result models
- reporting helpers

## Phase 3: Domain Services

Implement initial service families:

- hardening service
- segmentation service
- shared compliance summary support

Delay broad routing coverage until the first dual-path slice is stable.

## Phase 4: Expanded Validations

Add:

- routing validations
- drift/compliance comparisons
- integration tests that correlate intended and observed state
- curated suite tests

## Guardrails

- keep the repository local-only for now
- do not connect a remote yet
- do not overbuild the first slice
- keep lab artifacts demo-safe and reproducible
- prefer normalized result contracts over ad hoc dictionaries once real modules start appearing
