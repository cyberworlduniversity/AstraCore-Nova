# AstraCore Nova — Independent Architecture Prototype

## Research objective

Explore a new, inspectable computational path for an AI agent that does not depend on tokenizers, Transformer models, pretrained weights, or external model APIs. The current implementation is a research prototype, not a claim of general intelligence or proven architectural novelty.

## Prototype design: Relational Field State (RFS)

RFS treats input as a stream of Unicode code points. A bounded state field is updated by position-sensitive input signals and local neighbour interactions. A separate episodic store keeps source examples and their signatures. Retrieval is exact deterministic similarity ranking; it is not semantic understanding.

The agent pipeline is deliberately explicit:

1. Normalize and validate the incoming text without splitting it into tokens.
2. Encode the raw Unicode stream into a fixed-width field state.
3. Retrieve a small set of related stored episodes.
4. Build a transparent response from retrieved evidence and deterministic rules.
5. Mark unsupported requests as unknown rather than fabricate facts.
6. Store the interaction only when the caller explicitly enables learning.

## Current limitations

- No gradient-based learning or trained language model exists yet.
- No open-ended fluent text generation, reliable translation, or general reasoning.
- Similarity scores are mathematical comparisons, not semantic confidence.
- The first memory implementation is in-process and bounded.
- No network server, authentication, tools, or autonomous execution is included.

## Research gates

Before claiming progress, measure retrieval quality against baselines (exact match, character n-gram, and random ranking), include Tamil and English test sets, report latency and memory, and test adversarial inputs. A new name or formula alone does not establish novelty. Publish reproducible experiments and negative results.

## Run

```bash
python -m unittest discover -s tests -v
python demo.py
```

Python 3.10+, standard library only.


## v0.3 research direction: NFD Tri-Ledger Dynamics

The next experiment is documented in NFD_TRI_LEDGER_DESIGN.md and implemented
in nova_core/nfd_dynamics.py. It adds three coupled state ledgers: activation,
temporal trace, and prediction-error tension. A bounded surprise-gated local
adaptation rule updates the system as it consumes raw Unicode scalar events.

This is not evidence of a globally unprecedented architecture. Related work
exists in dynamical systems, predictive processing, and associative memory.
The new mechanism must be evaluated with ablations and baselines before any
novelty claim. It does not yet understand language or reason generally.
