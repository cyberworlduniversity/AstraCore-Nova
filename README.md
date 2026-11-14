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
- Expanded deterministic English relation grammar with 12 explicit patterns.
- English patterns for family relations, friendship, marriage, residence/location, employment, knowledge, ownership, and preferences.
- Deterministic positive-Horn forward chaining with proof traces and resource limits.
- Bounded fact memory with evidence IDs, source provenance, duplicate consolidation, and configurable contradiction reporting.
- Versioned JSON persistence with strict load validation and atomic file replacement.
- EnglishKnowledgeEngine connecting extraction, memory, and inference.
- Interactive English CLI and JSON-output demonstration.

## Requirements and quick start

Python 3.10 or newer. No package installation is required.

```bash
python -m unittest discover -s tests -v
python -m nova_core.validation
python -m nova_core --memory nova-memory.json
python english_demo.py
python english_demo.py "Arun is the father of Maya. Maya is the mother of Ravi."
```

The interactive CLI accepts supported English statements and commands:
`:facts`, `:save`, `:load`, `:help`, and `:quit`. It saves changed memory on exit.

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

To restore a saved snapshot, call `engine.load_memory("nova-memory.json")`. The file is versioned JSON; malformed or unsupported snapshots are rejected.

## Supported English sentence patterns

The extractor matches complete, explicit forms such as:

- `Arun is the father of Maya.`
- `Meena is the mother of Ravi.`
- `Arun is a parent of Maya.`
- `Maya is a friend of Arun.`
- `Arun is married to Meena.`
- `Maya lives in Chennai.` / `Ravi resides in Vellore.`
- `CWU is located in India.`
- `Hemanathan works at CWU.` / `Maya is employed at Acme Labs.`
- `Arun knows Ravi.`
- `Maya owns a laptop.`
- `Ravi likes science.` / `Meena loves music.`

Only the documented complete patterns are extracted. Negated, uncertain, question-form, or otherwise unsupported sentences are not converted into positive facts. Unsupported sentences produce no guessed facts. The reasoner currently derives parent and grandparent relations from explicit family facts; it does not infer arbitrary relationships. Contradiction detection requires caller-configured opposing predicates and preserves both sides.

## Validation and limitations

GitHub Actions validates the test suite on Python 3.10, 3.11, 3.12, and 3.13 and runs the NFD validation benchmark. The extended English grammar has dedicated regression tests for supported patterns, unsupported/negative inputs, self-relations, verbalization, and multi-sentence extraction. Passing tests proves the tested software behavior only. Synthetic ablations and microbenchmarks are not semantic-language benchmarks. Similarity scores are not semantic confidence.

This remains a research prototype, not a production-ready autonomous AI application. It does not provide arbitrary English understanding, open-domain fluent generation, network APIs, authentication, web access, or autonomous tool execution. The interactive CLI and JSON demo are local interfaces, not a deployed service.

## Language scope

Sentence extraction, examples, and user-facing demonstrations are English-only in this phase. The low-level Unicode event-processing primitive remains language-agnostic. Tamil-specific sentence patterns and tests are deferred to a later phase.

No claim of general intelligence, human-level reasoning, or global architectural novelty is made. Compare against documented baselines and conduct literature/prior-art review before making research novelty claims.
