# NFD Tri-Ledger Dynamics — Research Design v0.3

## Purpose

This document specifies a new experimental direction for Nova Field Dynamics
(NFD). The implementation is an original project prototype, but no claim is
made that the underlying ideas are globally unprecedented. A literature and
prior-art review is required before making a novelty claim.

## Core hypothesis

Treat input as a continuous stream of Unicode scalar events and maintain
three coupled, inspectable state ledgers rather than a token sequence or
learned embedding table:

1. **Activation ledger (A):** the current bounded state of the system.
2. **Temporal trace ledger (T):** a decaying record of previous activation.
3. **Tension ledger (E):** accumulated prediction-error energy.

For event c at step t, a direct continuous phase signal D(c,t) is computed
from the Unicode scalar and event position. A local prediction P is formed
from prior activation and a bounded adaptive bias. The residual R = D - P
determines surprise. Surprise gates a local plasticity update. The next
activation is a bounded nonlinear combination of current activation,
neighbour coupling, input drive, temporal trace, and tension suppression.

The reference implementation is in nova_core/nfd_dynamics.py.

## Why this is a research hypothesis, not a proven breakthrough

Dynamical systems, predictive processing, online adaptation, associative
memory, and event-driven computation all have substantial prior art. For
example, reservoir-computing systems have been used for dynamical associative
memory and attractor retrieval (Kong, Brewer & Lai, Nature Communications,
2024: https://doi.org/10.1038/s41467-024-49190-4). The present prototype
does not use that paper's reservoir architecture, but related work means
broad claims such as "nobody has done this" are not justified.

The specific combination and update rule in this repository need systematic
comparison against prior work. A distinct name or implementation is not by
itself evidence of scientific novelty.

## Explicit exclusions

- No tokenizer, token IDs, subword vocabulary, or embedding lookup table.
- No Transformer, RNN, reservoir neural network, pretrained model, or external
  AI inference API in this prototype.
- No third-party runtime dependency.
- Unicode code points are raw input events, not vocabulary IDs.

## Current scope and limitations

The implementation provides deterministic event processing, bounded ledgers,
a hand-designed local prediction-error update, and resettable state. It does
not yet perform semantic language understanding, general reasoning, reliable
language generation, or validated self-directed learning. The bias update is
a small adaptive mechanism, not evidence of intelligence.

## Required experiments before advancing

- Run the full unit-test suite in CI on supported Python versions.
- Compare against the existing NFD field encoder, exact-match recall,
  character n-gram similarity, and random baselines.
- Test Tamil and English separately and in mixed scripts.
- Measure order sensitivity, noise robustness, memory/runtime scaling,
  forgetting, and repeated-observation effects.
- Ablate each ledger (A, T, E) to determine whether it contributes measurable
  value.
- Publish configurations, datasets, seeds, metrics, and negative results.
- Conduct a broader literature and patent review before claiming novelty.

## Status

v0.3 research implementation only. Tests are authored but must pass in CI
before this design is considered validated.
