# NFD v0.4 — Experimental Validation

This phase adds reproducible standard-library-only measurements for the current
v0.3 engine. It does not change the core update equations.

## Run

```bash
python -m unittest discover -s tests -v
python -m nova_core.validation
```

## Measurements

- Adaptation: compares the normal local bias update with a frozen-bias control.
  Reports bias L1 magnitude and final activation-state delta.
- Ablation: compares the full engine with temporal-trace, tension, and
  adaptation mechanisms disabled one at a time.
- Microbenchmark: reports processed Unicode code-point events, elapsed wall
  time, throughput, peak traced Python memory, and final-state magnitudes.
- Corpus: deterministic synthetic English, Tamil, and mixed-script examples.

## Interpretation limits

These are controlled software experiments, not semantic-language benchmarks.
The ablations are mechanism-level controls; the activation ledger remains the
engine's state substrate and is not independently removable in this phase.
Runtime and memory values are machine-dependent. Do not compare runs from
different machines as if they were controlled results. No claim of general
reasoning, fluent generation, or architectural novelty follows from passing
these tests.

## Promotion gate

All unit tests and the Python 3.10–3.13 CI matrix must pass. Record the exact
commit, interpreter, hardware, corpus, repetitions, and output JSON before
using any performance claim. NFD v0.5 reasoning work must wait until these
results have been reviewed.
