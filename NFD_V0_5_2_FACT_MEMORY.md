# NFD v0.5.2 — English Fact Memory and Contradiction Detection

## Scope

Adds a bounded in-process memory for explicitly structured facts. Every fact
has a stable insertion evidence ID and one or more source labels. Repeated
facts are deduplicated while source provenance is merged deterministically.

## Contradiction policy

Contradictions are domain-defined, not guessed. Callers configure opposing
predicate pairs, for example active/inactive. A conflict is reported only
when the predicates are configured as opposites and all arguments and arity
match. Both evidence records remain in memory. The system never chooses a
winner, deletes a fact, or silently overwrites evidence.

Predicates such as father and mother are not assumed to contradict one
another. A person can satisfy both relations in different contexts.

## Resource and safety properties

- Capacity is bounded and validated.
- When full, insertion fails explicitly; existing evidence is not evicted.
- Duplicate facts merge source labels and retain the original evidence ID.
- Conflict reports are deterministic.
- Facts and source labels are opaque strings; this component does not parse
  ordinary English or infer facts from prose.
- No tokenizer, token IDs, embeddings, neural model, Transformer, pretrained
  model, third-party dependency, or external AI API is used.

## Example

    from nova_core.fact_memory import FactMemory
    memory = FactMemory(contradiction_pairs=(("active", "inactive"),))
    memory.add(("active", "account-7"), "audit-2026-01")
    memory.add(("inactive", "account-7"), "audit-2026-02")
    report = memory.report()
    print(report.conflicts)

## Validation

Run: python -m unittest discover -s tests -v

Tests cover provenance, duplicate handling, explicit opposing predicates,
non-conflicting relations, bounded capacity, invalid input, and determinism.

## Limitations

This is a structured fact store, not persistent disk storage or automatic
English knowledge extraction. It does not establish truth: source labels are
caller-supplied metadata. Contradiction detection is only as complete as the
caller-provided predicate policy.
