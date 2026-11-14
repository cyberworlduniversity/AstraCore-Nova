# AstraCore Nova — Prototype Build 0.2

This branch adds an independent research scaffold alongside the existing NFD experiment. It does not replace or import the original AstraCore code.

## Design constraints
- Raw Unicode code-point input; no tokenizer or token IDs.
- No Transformer, neural-network framework, pretrained weights, or external AI API.
- Python standard library only.
- Explicit bounded memory and evidence-aware responses.
- Unknown answers are reported as unknown.

## Run
```bash
python -m unittest discover -s tests -v
python nova_demo.py
```

## What this build proves
It proves that the package, deterministic field transform, bounded episodic store, and conservative agent shell execute as software. It does **not** prove general intelligence, semantic understanding, learning from data, fluent generation, or architectural novelty.

## Next research milestones
1. Establish retrieval baselines and Tamil/English evaluation corpus.
2. Measure latency, memory, collision behaviour, and robustness.
3. Design an explicit online learning rule and test for catastrophic interference.
4. Add structured planning only after measurable state/retrieval performance.
5. Add controlled tool execution with permissions and audit logs.
6. Consider language generation only after evaluation demonstrates useful predictive structure.
