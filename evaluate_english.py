"""Evaluate the bounded English extractor against a curated JSON corpus."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from nova_core.fact_extraction import EnglishFactExtractor


def evaluate(path: str | Path) -> dict:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != "astracore-nova-english-pattern-evaluation" or payload.get("version") != 1:
        raise ValueError("unsupported evaluation corpus schema")
    examples = payload.get("examples")
    if not isinstance(examples, list) or not examples:
        raise ValueError("evaluation corpus must contain a non-empty examples list")

    extractor = EnglishFactExtractor()
    tp = fp = fn = exact_sentences = 0
    supported_tp = supported_fp = supported_fn = 0
    rows = []
    for index, item in enumerate(examples):
        if not isinstance(item, dict) or not isinstance(item.get("sentence"), str):
            raise ValueError(f"invalid evaluation example at index {index}")
        expected = item.get("expected_facts")
        if not isinstance(expected, list):
            raise ValueError(f"expected_facts must be a list at index {index}")
        expected_set = {tuple(fact) for fact in expected}
        if any(len(fact) != 3 or not all(isinstance(x, str) for x in fact) for fact in expected_set):
            raise ValueError(f"facts must be three-string relation tuples at index {index}")
        result = extractor.extract(item["sentence"])
        predicted_set = set(result.facts)
        correct = predicted_set & expected_set
        tp += len(correct)
        fp += len(predicted_set - expected_set)
        fn += len(expected_set - predicted_set)
        exact = predicted_set == expected_set
        exact_sentences += int(exact)
        expected_supported = bool(expected_set)
        if result.supported and expected_supported:
            supported_tp += 1
        elif result.supported and not expected_supported:
            supported_fp += 1
        elif not result.supported and expected_supported:
            supported_fn += 1
        rows.append({
            "sentence": item["sentence"],
            "expected_facts": [list(fact) for fact in sorted(expected_set)],
            "predicted_facts": [list(fact) for fact in sorted(predicted_set)],
            "exact_match": exact,
        })

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    class_precision = supported_tp / (supported_tp + supported_fp) if supported_tp + supported_fp else 0.0
    class_recall = supported_tp / (supported_tp + supported_fn) if supported_tp + supported_fn else 0.0
    class_f1 = (
        2 * class_precision * class_recall / (class_precision + class_recall)
        if class_precision + class_recall else 0.0
    )
    return {
        "schema": "astracore-nova-english-pattern-evaluation-results",
        "examples": len(examples),
        "exact_sentence_matches": exact_sentences,
        "sentence_exact_match_rate": exact_sentences / len(examples),
        "fact": {"true_positive": tp, "false_positive": fp, "false_negative": fn,
                 "precision": precision, "recall": recall, "f1": f1},
        "supported_classification": {
            "true_positive": supported_tp, "false_positive": supported_fp,
            "false_negative": supported_fn, "precision": class_precision,
            "recall": class_recall, "f1": class_f1,
        },
        "warning": "Curated pattern-conformance corpus only; not a representative English benchmark.",
        "examples_detail": rows,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus", default="evaluation/english_pattern_eval.json",
        help="Path to the curated evaluation JSON corpus",
    )
    parser.add_argument("--output", help="Optional path for the JSON report")
    args = parser.parse_args(argv)
    report = evaluate(args.corpus)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
