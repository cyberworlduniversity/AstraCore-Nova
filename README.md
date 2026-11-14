# AstraCore Nova — English-First NFD Prototype

A clean-room research prototype exploring a deterministic, non-token, non-Transformer computation path. The implementation uses Python standard-library components only.

## Hard architecture exclusions
- No tokenizer, token IDs, subword vocabulary, or embedding lookup table.
- No NCM, Transformer, RNN, neural-network framework, or pretrained model.
- No external AI inference API or third-party runtime dependency.
- Raw Unicode code points are consumed directly by the field-dynamics experiments.

## Current components
- NFD field encoding and bounded similarity-based episodic recall.
- Tri-ledger dynamics with activation, temporal trace, prediction-error tension, and bounded local adaptation.
- Narrow English sentence-pattern extraction for parent, father, mother, and friend relations.
- Deterministic positive-Horn forward chaining with proof traces and resource limits.
- Bounded fact memory with source provenance, duplicate consolidation, and configurable contradiction reporting.
- EnglishKnowledgeEngine connecting extraction, memory, and inference.

## Quick start

```bash
python -m unittest discover -s tests -v
python demo.py
python nova_demo.py
python -m nova_core.validation
```

Requires Python 3.10 or newer. No package installation is required.

## English knowledge pipeline

```python
from nova_core import EnglishKnowledgeEngine

engine = EnglishKnowledgeEngine()
result = engine.process(
    "Arun is the father of Maya. Maya is the mother of Ravi.",
    source="example-source"
)
print(result.reasoning.facts)
print(result.memory.conflicts)
```

Only explicitly supported complete English sentence patterns are extracted. Unsupported text produces no inferred fact. The fact reasoner consumes structured facts and rules; it is not a general natural-language understanding engine.

## Validation and limits

CI tests target Python 3.10–3.13. Synthetic ablations and microbenchmarks measure software mechanisms, not semantic intelligence. Similarity scores are not semantic confidence. The current agent shell is conservative and retrieval-based; broad open-domain answers, reliable fluent generation, persistent storage, web access, and autonomous tool use are not implemented.

Passing tests proves the tested software behavior only. It does not establish general intelligence, human-level reasoning, or global architectural novelty. Compare against documented baselines and conduct literature/prior-art review before making research novelty claims.

## Language scope

This development phase is English-only at the sentence extraction and user-facing demo layers. The low-level Unicode event-processing primitive remains language-agnostic. Tamil-specific sentence patterns and test examples are deferred to a later phase.
