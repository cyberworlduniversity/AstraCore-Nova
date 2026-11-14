# AstraCore Nova — Independent Architecture Prototype

## Research objective

Explore an inspectable computation path without tokenizers, Transformer models, pretrained weights, or external model APIs. This is a research prototype, not a claim of general intelligence or proven architectural novelty.

## Implemented components

1. Raw Unicode code-point field encoding and bounded state dynamics.
2. Bounded episodic similarity retrieval.
3. English-only deterministic sentence-pattern extraction for a small set of explicit relations.
4. Positive-Horn forward chaining over supplied structured facts, with proof traces.
5. Bounded fact memory with provenance, duplicate consolidation, and configured contradiction alerts.
6. An EnglishKnowledgeEngine that connects extraction, memory, and reasoning.

## End-to-end flow

1. Validate English text and split only at explicit sentence punctuation.
2. Match supported complete sentence patterns; unsupported text yields no fact.
3. Store extracted facts with source labels.
4. Apply explicit symbolic rules to the accumulated fact set.
5. Preserve proof steps and store derived facts with rule provenance.
6. Report configured opposing facts without silently choosing a winner.

## Current limitations

- English extraction coverage is narrow and pattern-based.
- No arbitrary natural-language understanding or open-ended fluent generation.
- No persistent database, server/API, authentication, browser access, or autonomous tools.
- Similarity scores are mathematical comparisons, not semantic confidence.
- Memory is in-process and bounded.
- No self-directed learning or verified general reasoning.

## Research gates

Compare retrieval against exact-match, character n-gram, and random baselines. Evaluate extraction precision/recall on manually labelled held-out English examples. Measure proof validity, contradiction policy coverage, latency, memory, collisions, and adversarial inputs. A new name or formula alone does not establish novelty. Publish reproducible experiments and negative results.

Python 3.10+, standard library only.
