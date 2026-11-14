"""Runnable English-only end-to-end AstraCore Nova prototype demo.

Run:
    python english_demo.py
    python english_demo.py "Arun is the father of Maya. Maya is the mother of Ravi."
    python english_demo.py --source notes-01 "Arun is the father of Maya."
"""
from __future__ import annotations

import argparse
import json

from nova_core import EnglishKnowledgeEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the deterministic English fact-memory and reasoning prototype."
    )
    parser.add_argument(
        "text",
        nargs="?",
        default=(
            "Arun is the father of Maya. "
            "Maya is the mother of Ravi."
        ),
        help="English sentences using the documented supported relation patterns.",
    )
    parser.add_argument(
        "--source",
        default="demo-input",
        help="Evidence label attached to facts extracted from this input.",
    )
    parser.add_argument(
        "--capacity",
        type=int,
        default=1000,
        help="Maximum number of unique facts retained in in-process memory.",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=32,
        help="Maximum forward-chaining inference rounds.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        engine = EnglishKnowledgeEngine(
            capacity=args.capacity,
            max_rounds=args.max_rounds,
        )
        result = engine.process(args.text, source=args.source)
    except (TypeError, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2

    payload = {
        "ok": True,
        "scope": "English-only deterministic research prototype",
        "limitations": [
            "Only documented complete English sentence patterns are extracted.",
            "Unsupported sentences produce no guessed facts.",
            "Reasoning is bounded positive-Horn inference over structured facts.",
            "Memory exists only for this process and is not persistent.",
            "This is not general language understanding or an LLM.",
        ],
        "extraction": [
            {
                "input": item.source,
                "supported": item.supported,
                "pattern": item.pattern,
                "facts": [list(fact) for fact in item.facts],
                "reason": item.reason,
            }
            for item in result.extraction
        ],
        "reasoning": {
            "facts": [list(fact) for fact in result.reasoning.facts],
            "derived": [list(fact) for fact in result.reasoning.derived],
            "proof": [
                {
                    "fact": list(step.fact),
                    "rule": step.rule_name,
                    "premises": [list(fact) for fact in step.premises],
                }
                for step in result.reasoning.proof
            ],
            "rounds": result.reasoning.rounds,
            "saturated": result.reasoning.saturated,
        },
        "memory": {
            "capacity": engine.memory.capacity,
            "fact_count": len(result.memory.facts),
            "duplicate_count": result.memory.duplicates,
            "facts": [
                {
                    "evidence_id": item.evidence_id,
                    "fact": list(item.fact),
                    "sources": list(item.sources),
                }
                for item in result.memory.facts
            ],
            "conflicts": [
                {
                    "left": list(item.left.fact),
                    "right": list(item.right.fact),
                    "reason": item.reason,
                }
                for item in result.memory.conflicts
            ],
        },
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if result.reasoning.saturated else 1


if __name__ == "__main__":
    raise SystemExit(main())
