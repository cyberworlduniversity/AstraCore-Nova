# NFD v0.5.1 — Multilingual Fact Extraction

## Scope

This increment adds a transparent sentence-pattern adapter between raw text
and the v0.5 structured fact reasoner. It supports a deliberately narrow set
of explicit relation statements in English and Tamil. It is not general NLP,
not a tokenizer, and not a claim of arbitrary sentence understanding.

## Supported examples

- English: `Arun is the father of Maya.`
- English: `Meena is the mother of Ravi.`
- English: `Maya is a friend of Arun.`
- English: `Arun is a parent of Maya.`
- Tamil: `அருண் மாயாவின் தந்தை.`
- Tamil: `மீனா ரவியின் தாய்`

Names and multi-word spans are captured as whole strings. The implementation
uses complete regular-expression patterns; it does not split text into words
or assign token IDs. Unmatched sentences return an unsupported result and
produce no facts.

## Pipeline

1. Validate and trim the supplied sentence.
2. Match one supported complete sentence pattern.
3. Emit a structured relation tuple such as `(father, Arun, Maya)`.
4. Apply explicit inference rules, e.g. father implies parent.
5. For multi-sentence input, split only at explicit sentence punctuation; do not tokenize words.
6. Combine extracted facts and run bounded inference across sentence boundaries.
7. Return facts and proof steps with the extraction pattern identifier.
8. Render a result only through fixed Tamil or English templates.

## Validation

Run `python -m unittest discover -s tests -v`.
Tests cover English and Tamil patterns, inference and proof traces, fixed
verbalization, and the rule that unsupported sentences are never guessed.

## Limitations

Coverage is intentionally narrow. It does not handle arbitrary word order,
negation, questions, pronouns, tense, complex morphology, ambiguity, or
multi-sentence discourse. Tamil suffix handling is limited to the listed
templates. The output is a structured fact/proof, not a free-form answer.
Evaluate on manually labelled, held-out Tamil and English data before
expanding coverage or making language-understanding claims.

## Multi-sentence reasoning

`extract_many(text)` returns one extraction result per punctuation-delimited sentence. `reason_many(text)` combines only supported facts, derives parent relations from father/mother facts, and can infer a grandparent relation across two sentences. Unsupported sentences remain explicitly marked and contribute no facts. Example:

- `அருண் மாயாவின் தந்தை. மாயா ரவியின் தாய்.`
- Derived: `(grandparent, அருண், ரவி)` with a proof chain through both parent facts.

This is still a narrow pattern engine. Punctuation-based segmentation is not full discourse understanding.
