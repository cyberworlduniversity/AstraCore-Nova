# NFD v0.5 — Independent Reasoning Prototype

## Scope

Adds a deterministic positive-Horn forward-chaining reasoner alongside the
NFD v0.3 dynamics. It consumes explicitly supplied structured English facts
and rules. Symbols are opaque strings; multi-word English values remain
intact. The engine does not split strings or tokenize input.

This is an independent symbolic inference component, not automatic natural
language understanding and not a fluent language generator.

## Example

    from nova_core.reasoning import IndependentReasoner, Rule
    engine = IndependentReasoner()
    engine.add_fact(("parent", "Arun", "Maya"))
    engine.add_fact(("parent", "Maya", "Ravi"))
    engine.add_rule(Rule("grandparent",
        (("parent", "?x", "?y"), ("parent", "?y", "?z")),
        ("grandparent", "?x", "?z")))
    result = engine.infer()
    print(("grandparent", "Arun", "Ravi") in result.facts)

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
deterministic output, English multi-word values, and resource bounds.

## Limitations

The engine reasons only over facts and rules supplied in structured form.
It does not independently understand arbitrary English prose. English
sentence extraction is a separate narrow pattern-based component. Evaluate
precision, recall, proof validity, contradiction handling, and generalization
on held-out examples before making broader language claims.
