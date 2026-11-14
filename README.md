# AstraCore Nova — Independent Prototype 0.1

A clean-room experimental prototype for a non-token, non-Transformer computation path.

## Explicit exclusions
- No AASTA or other tokenizer.
- No NCM implementation or dependency.
- No Transformer, neural-network framework, pretrained model, or copied AstraCore implementation.
- No external Python packages. The prototype uses Python's standard library only.

## Prototype idea: Nova Field Dynamics (NFD)
NFD consumes the original Unicode character stream directly. Each code point perturbs a bounded numerical field using position-dependent phase functions and a coupled nonlinear update. The final field is a compact state signature. A small associative store can compare signatures and retrieve previously stored examples.

This is an experimental computational mechanism, not a trained language model. It does not yet understand arbitrary language, reason generally, translate reliably, or generate fluent answers. Similarity retrieval is a measurable first experiment, not proof of intelligence or novelty.

## Requirements
- Python 3.10+
- No third-party dependencies

## Run
```bash
python demo.py
python -m unittest discover -s tests -v
```

## Research rules
1. Keep this prototype isolated from the existing AstraCore repository.
2. Do not import tokenizer, NCM, Transformer, or pretrained-model code.
3. Record memory, runtime, and retrieval quality before expanding the architecture.
4. Treat all performance and novelty claims as unverified until compared against documented baselines.

## Current status
Prototype 0.1: deterministic field encoding and bounded associative recall. No model training has occurred.


## NFD research engine v0.3

The branch also includes an experimental tri-ledger event engine in
nova_core/nfd_dynamics.py. It maintains activation, temporal-trace, and
prediction-error-tension ledgers and applies a bounded local adaptation rule
while consuming Unicode code points directly. See NFD_TRI_LEDGER_DESIGN.md.

This is a research mechanism, not a language model. It does not yet provide
semantic understanding, general reasoning, or fluent generation. Its novelty
is unproven and must be evaluated against prior work and reproducible baselines.
