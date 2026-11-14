# AstraCore Nova — English-First NFD Prototype

A clean-room research prototype exploring a deterministic, non-token, non-Transformer computation path. The implementation uses Python standard-library components only.

## Hard architecture exclusions
- No tokenizer, token IDs, subword vocabulary, or embedding lookup table.
- No NCM, Transformer, RNN, neural-network framework, or pretrained model.
- No external AI inference API or third-party runtime dependency.
- Raw Unicode code points are consumed directly by the field-dynamics experiments.

## Implemented components
- NFD field encoding and bounded similarity-based episodic recall.
- Tri-ledger dynamics with activation, temporal trace, prediction-error tension, and bounded local adaptation.
- Narrow English sentence-pattern extraction for parent, father, mother, and friend relations.
- Deterministic positive-Horn forward chaining with proof traces and resource limits.
- Bounded in-process fact memory with source provenance, duplicate consolidation, and configurable contradiction reporting.
- EnglishKnowledgeEngine connecting extraction, memory, and inference.
- Runnable JSON-output end-to-end demonstration in `english_demo.py`.

## Quick start

Requires Python 3.10 or newer. No package installation is required.

```bash
python -m unittest discover -s tests -v
python -m nova_core.validation
python english_demo.py
python english_demo.py "Arun is the father of Maya. Maya is the mother of Ravi."
```

## English knowledge pipeline

```python
from nova_core import EnglishKnowledgeEngine

engine = EnglishKnowledgeEngine()
result = engine.process(
    "Arun is the father of Maya. Maya is the mother of Ravi.",
    source="example-source"
)
print(result.reasoning.facts)
print(result.reasoning.proof)
print(result.memory.conflicts)
engine.save_memory("nova-memory.json")
```

The CLI emits JSON containing extraction decisions, structured facts, derived facts, proof steps, memory evidence, and configured conflicts. Unsupported sentences are reported and never guessed.

## Supported English sentence patterns

- `Arun is the father of Maya.`
- `Meena is the mother of Ravi.`
- `Maya is a friend of Arun.`
- `Arun is a parent of Maya.`

The extractor intentionally supports a narrow set of complete sentence forms. The reasoner consumes structured facts and explicit rules; it is not a general natural-language understanding engine.

## Validation and limitations

CI tests target Python 3.10–3.13. Synthetic ablations and microbenchmarks measure software mechanisms, not semantic intelligence. Similarity scores are not semantic confidence. Fact memory is in-process and bounded; it is not persistent across process restarts. Contradiction detection requires caller-configured opposing predicates. The prototype does not provide arbitrary English understanding, open-domain fluent generation, authentication, network APIs, web access, or autonomous tool use.

Passing tests proves the tested software behavior only. It does not establish general intelligence, human-level reasoning, or global architectural novelty. Compare against documented baselines and conduct literature/prior-art review before making research novelty claims.

## Language scope

This development phase is English-only at the sentence extraction and user-facing demo layers. The low-level Unicode event-processing primitive remains language-agnostic. Tamil-specific sentence patterns and test examples are deferred to a later phase.
