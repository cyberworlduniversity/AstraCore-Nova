# Production Readiness Plan — AstraCore Nova

Status date: 2026-11-14  
Current status: research prototype; **not production-ready**.

This document defines the engineering gates required before calling AstraCore Nova a production release. Passing the current unit tests is necessary but is not sufficient.

## Current verified baseline

- English-only deterministic extraction with 12 explicitly documented relation patterns.
- Bounded positive-Horn inference with inspectable proof traces.
- Fact memory with source provenance, duplicate consolidation, configured conflict reporting, and versioned JSON persistence.
- Interactive local CLI and JSON demonstration.
- No tokenizer, token IDs, NCM, Transformer, RNN, pretrained model, neural-network framework, or external AI inference API.
- Latest CI run: Python 3.10, 3.11, 3.12, and 3.13 test jobs passed; NFD validation benchmark passed.
- The current CI suite ran 79 tests successfully.
- The NFD benchmark artifact is a synthetic microbenchmark, not an English-language quality evaluation.

## Production gates

### Gate 1 — Product and runtime contract
- Define supported operating systems, Python versions, installation method, data location, backup policy, and whether the first release is local single-user or hosted multi-user.
- Freeze public interfaces and version the memory format and API contract.
- Provide deterministic startup, shutdown, health reporting, and upgrade/rollback behavior.

### Gate 2 — Data integrity and memory safety
- Add crash-recovery tests for interrupted writes and corrupted snapshots.
- Add file locking or an explicit single-writer guarantee.
- Add schema migration tests and documented export/import procedures.
- Verify that one user's memory cannot be read by another user before any multi-user mode is introduced.

### Gate 3 — Input and reasoning safety
- Enforce input byte, sentence, fact, inference-round, and memory limits at every public boundary.
- Reject malformed Unicode, control characters where unsafe, oversized inputs, and ambiguous unsupported claims.
- Preserve provenance through every derived fact and proof step.
- Do not silently resolve contradictions or present heuristic similarity as semantic certainty.

### Gate 4 — Service and authentication (only if hosted API is selected)
- Use a production-grade HTTP server and TLS termination; do not expose Python's development HTTP server directly.
- Implement authentication, authorization, request limits, timeouts, CORS allow-listing, structured error responses, and secret rotation.
- Add tenant isolation and audit events before multi-user access.
- Store secrets outside source control and test that logs never contain credentials or private user text.

### Gate 5 — Operations
- Structured logs with request IDs and redaction.
- Health/readiness endpoints and actionable metrics.
- Automated backups, restore drills, retention rules, and rollback procedure.
- Dependency and source scanning, reproducible builds, release checksums, and vulnerability response process.
- Load, soak, fuzz, malformed-input, and adversarial regression testing.

### Gate 6 — Release evidence
- CI green on every supported runtime.
- Reproducible benchmark reports with hardware/runtime details and raw output.
- English evaluation corpus with train/dev/test separation, annotation rules, precision/recall/F1, contradiction and uncertainty cases, and baseline comparisons.
- Independent review of security, data integrity, and research claims.
- Versioned release, changelog, installation guide, operator guide, and known-limitations statement.

## Immediate engineering sequence

1. Finish the English grammar and inference regression suite; keep all unsupported/negated/uncertain claims conservative.
2. Expand the evaluation corpus and publish extraction metrics rather than describing pattern coverage as general language understanding.
3. Harden persistence and add corruption/crash/concurrency tests.
4. Package and document a local single-user release first; keep network access disabled by default.
5. Only after the local release is stable, select a hosting target and implement the hosted service, authentication, tenant isolation, monitoring, backup, and deployment pipeline.
6. Run release-candidate security and recovery tests.
7. Freeze the implementation and write the final research paper from reproducible results, including negative results and limitations.

## External release dependencies

A live hosted deployment cannot be completed safely without a selected hosting target, a deployment account with appropriate permissions, and user-controlled secrets/domain settings where applicable. No credentials should be pasted into source files or committed to Git. The repository can be prepared and tested without those secrets, but deployment must remain blocked until the required account-side configuration exists.

## Release decision rule

Do not label the project production-ready while any required gate is open. A green unit-test matrix verifies the tested code paths only; it does not establish operational security, reliability under load, language understanding, or production readiness.
