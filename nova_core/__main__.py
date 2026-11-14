"""Interactive English-first command-line interface for AstraCore Nova."""
from __future__ import annotations

import argparse
from pathlib import Path

from .fact_extraction import verbalize_fact
from .knowledge import EnglishKnowledgeEngine


def _format_fact(fact):
    try:
        return verbalize_fact(fact)
    except ValueError:
        return " ".join(fact)


def main(argv=None):
    parser = argparse.ArgumentParser(description="AstraCore Nova English knowledge prototype")
    parser.add_argument(
        "--memory", default="nova-memory.json",
        help="JSON file used to persist fact memory (default: nova-memory.json)",
    )
    args = parser.parse_args(argv)
    memory_path = Path(args.memory)
    engine = EnglishKnowledgeEngine()

    if memory_path.exists():
        try:
            engine.load_memory(memory_path)
            print(f"Loaded {len(engine.memory)} fact records from {memory_path}.")
        except (OSError, ValueError) as exc:
            parser.error(f"could not load memory: {exc}")

    print("AstraCore Nova — English knowledge prototype")
    print("Enter supported statements. Commands: :facts, :save, :load, :help, :quit")
    print("Example: Arun is the father of Maya.")

    dirty = False
    while True:
        try:
            line = input("nova> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line == ":quit":
            break
        if line == ":help":
            print("Supported patterns: X is the father of Y; X is the mother of Y;")
            print("X is a parent of Y; X is a friend of Y.")
            print(":facts lists stored facts; :save writes JSON; :load restores JSON; :quit exits.")
            continue
        if line == ":facts":
            if not engine.memory.facts:
                print("No facts stored.")
            for record in engine.memory.facts:
                print(f"[{record.evidence_id}] {_format_fact(record.fact)}")
                print("    sources: " + ", ".join(record.sources))
            continue
        if line == ":save":
            try:
                engine.save_memory(memory_path)
                dirty = False
                print(f"Saved {len(engine.memory)} fact records to {memory_path}.")
            except OSError as exc:
                print(f"Save failed: {exc}")
            continue
        if line == ":load":
            try:
                report = engine.load_memory(memory_path)
                dirty = False
                print(f"Loaded {len(report.facts)} fact records from {memory_path}.")
            except (OSError, ValueError) as exc:
                print(f"Load failed: {exc}")
            continue

        try:
            result = engine.process(line, source="cli")
        except (ValueError, RuntimeError) as exc:
            print(f"Input could not be processed: {exc}")
            continue
        supported = [item for item in result.extraction if item.supported]
        if not supported:
            print("No supported English pattern matched. No fact was inferred.")
        else:
            for item in supported:
                for fact in item.facts:
                    print("Extracted:", _format_fact(fact))
            if result.reasoning.derived:
                print("Derived:")
                for fact in result.reasoning.derived:
                    print(" -", _format_fact(fact))
            dirty = True
        if result.memory.conflicts:
            print("Configured contradictions detected:")
            for conflict in result.memory.conflicts:
                print(" -", _format_fact(conflict.left.fact), "<->",
                      _format_fact(conflict.right.fact))

    if dirty:
        try:
            engine.save_memory(memory_path)
            print(f"Saved {len(engine.memory)} fact records to {memory_path}.")
        except OSError as exc:
            print(f"Exit save failed: {exc}")
    print("AstraCore Nova session ended.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
