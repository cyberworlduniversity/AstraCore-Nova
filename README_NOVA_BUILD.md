# AstraCore Nova — English-First Prototype Build 0.4

This branch contains an isolated research prototype with an English-first symbolic knowledge path. It does not replace or import the original AstraCore implementation.

## Design constraints
- Raw Unicode code-point input for the NFD field-dynamics experiment.
- No tokenizer, token IDs, or embedding lookup table.
- No Transformer, neural-network framework, pretrained weights, or external AI API.
- Python standard library only.
- Explicit bounded memory and evidence-aware responses.
- Unsupported English sentence forms produce no guessed facts.

## Run
```bash
python -m unittest discover -s tests -v
python -m nova_core.validation
python -m nova_core --memory nova-memory.json
python english_demo.py
```

## Implemented English path
1. Deterministic pattern extraction for a small set of explicit family/friend relations.
2. Structured fact storage with source provenance and duplicate consolidation.
3. Configurable contradiction alerts that preserve both sides of a conflict.
4. Bounded positive-Horn inference with inspectable proof steps.
5. Versioned JSON persistence with atomic writes and strict load validation.
6. An interactive CLI and JSON demonstration for local use.

## What this build proves
It proves only the tested software behavior: deterministic field updates, bounded stores, supported pattern extraction, structured inference, provenance handling, persistence round trips, and configured conflict reporting. It does not prove general intelligence, broad semantic understanding, autonomous learning, fluent generation, or architectural novelty.

## Remaining production gates
- Expand and benchmark English extraction on manually labelled held-out datasets.
- Add a production database with migrations, backup, and recovery tests.
- Add a documented application/API boundary, input limits, authentication, and audit logs before network exposure.
- Add permissioned tools only after sandbox and threat-model tests.
- Evaluate retrieval against exact-match, character n-gram, and random baselines.
- Complete security, performance, and prior-art reviews before a production or novelty claim.
