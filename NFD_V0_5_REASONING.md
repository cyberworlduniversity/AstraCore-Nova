# NFD v0.5 — Independent Reasoning Prototype

## Scope

Adds a deterministic positive-Horn forward-chaining reasoner alongside the
NFD v0.3 dynamics. It consumes explicitly supplied structured facts and rules.
Symbols are opaque strings and may contain Tamil, English, mixed-script, or
multi-word content. The engine never splits strings or tokenizes input.

This is an independent symbolic inference component, not automatic natural
language understanding and not a fluent language generator.

## Example

    from nova_core.reasoning import IndependentReasoner, Rule
    engine = IndependentReasoner()
    engine.add_fact(("parent", "அருண்", "மாயா"))
    engine.add_fact(("parent", "மாயா", "ரவி"))
    engine.add_rule(Rule("grandparent",
        (("parent", "?x", "?y"), ("parent", "?y", "?z")),
        ("grandparent", "?x", "?z")))
    result = engine.infer()
    print(("grandparent", "அருண்", "ரவி") in result.facts)

## Semantics and safety

- Facts are non-empty tuples of opaque string symbols.
- Variables use the explicit ?name convention.
- Rules are positive Horn clauses with one conclusion and one or more premises.
- Inference is deterministic, monotonic, and forward-chaining.
- Each derived fact includes its rule name and supporting premises.
- max_facts and max_rounds bound resource use.
- No negation, disjunction, probabilistic inference, code execution, parser,
  tokenizer, token IDs, embeddings, neural networks, pretrained models, or
  external inference APIs are used.

## Validation

Run: python -m unittest discover -s tests -v

Tests cover multi-hop inference, unification, repeated variables, proof traces,
deterministic output, Tamil/mixed Unicode symbols, and resource bounds.

## Limitations and next gates

The engine reasons only over facts and rules supplied in structured form. It
does not extract facts from ordinary Tamil or English sentences. Before
claiming language reasoning, build and evaluate a separate transparent
sentence-to-fact interface against manually labelled Tamil and English data.
Measure precision, recall, proof validity, contradiction handling, and
generalization on held-out examples. Do not describe this prototype as general
intelligence or natural-language understanding.
