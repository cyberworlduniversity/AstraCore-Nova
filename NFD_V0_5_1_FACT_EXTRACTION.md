# NFD v0.5.1 — English Fact Extraction

## Scope

This increment adds a transparent sentence-pattern adapter between raw text
and the v0.5 structured fact reasoner. It supports a deliberately narrow set
of explicit English relationship statements. It is not general NLP and is
not a tokenizer or a claim of arbitrary sentence understanding.

## Supported examples

- `Arun is the father of Maya.`
- `Meena is the mother of Ravi.`
- `Maya is a friend of Arun.`
- `Arun is a parent of Maya.`

Names and multi-word spans are captured as whole strings. The implementation
uses complete regular-expression patterns; it does not split text into words
or assign token IDs. Unmatched sentences return an unsupported result and
produce no facts.

## Pipeline

1. Validate and trim the supplied English sentence.
2. Match one supported complete sentence pattern.
3. Emit a structured relation tuple such as `(father, Arun, Maya)`.
4. Apply explicit inference rules, e.g. father implies parent.
5. For multi-sentence input, split only at explicit English sentence punctuation.
6. Combine extracted facts and run bounded inference across sentence boundaries.
7. Return facts and proof steps with the extraction pattern identifier.
8. Render results only through fixed English templates.

## Validation

Run `python -m unittest discover -s tests -v`.
Tests cover English patterns, inference and proof traces, fixed English
verbalization, and the rule that unsupported sentences are never guessed.

## Limitations

Coverage is intentionally narrow. It does not handle arbitrary word order,
negation, questions, pronouns, tense, ambiguity, or multi-sentence discourse.
Punctuation-based segmentation is not full discourse understanding. The
output is a structured fact/proof, not a free-form answer.
