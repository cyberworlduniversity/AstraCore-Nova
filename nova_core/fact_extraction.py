"""Transparent, bounded English sentence-pattern fact extraction.

This is not general NLP. It matches a small set of complete English sentence
forms. No tokenization, model, embedding, or external API is used.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .reasoning import Fact, IndependentReasoner, Rule


@dataclass(frozen=True)
class ExtractionResult:
    source: str
    facts: tuple[Fact, ...]
    language: str | None
    pattern: str | None
    supported: bool
    reason: str


class EnglishFactExtractor:
    """Extract a narrow set of explicit English family/friend relations."""

    _patterns = (
        ("english_parent", re.compile(
            r"^(?P<subject>.+?) is (?:a )?parent of (?P<object>.+?)$", re.I
        ), "parent"),
        ("english_father", re.compile(
            r"^(?P<subject>.+?) is (?:the )?father of (?P<object>.+?)$", re.I
        ), "father"),
        ("english_mother", re.compile(
            r"^(?P<subject>.+?) is (?:the )?mother of (?P<object>.+?)$", re.I
        ), "mother"),
        ("english_friend", re.compile(
            r"^(?P<subject>.+?) is (?:a )?friend of (?P<object>.+?)$", re.I
        ), "friend"),
    )

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"^[\s\u200b]+|[\s\u200b]+$", "", text).rstrip(".!?")

    def extract(self, sentence: str) -> ExtractionResult:
        if not isinstance(sentence, str) or not sentence.strip():
            raise ValueError("sentence must be a non-empty string")
        text = self._clean(sentence)
        for name, pattern, relation in self._patterns:
            match = pattern.fullmatch(text)
            if match:
                subject = self._clean(match.group("subject"))
                obj = self._clean(match.group("object"))
                if subject and obj:
                    return ExtractionResult(
                        sentence, ((relation, subject, obj),), "en", name, True,
                        "Extracted by an explicit deterministic English pattern.",
                    )
        return ExtractionResult(
            sentence, (), None, None, False,
            "No supported English sentence pattern matched; no facts inferred.",
        )

    def extract_many(self, text: str) -> tuple[ExtractionResult, ...]:
        """Extract sentences split only at explicit English punctuation."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")
        segments = [
            part.strip()
            for part in re.split(r"(?<=[.!?])\s+", text)
            if part.strip()
        ]
        if not segments:
            segments = [text.strip()]
        return tuple(self.extract(part) for part in segments)

    def reason_many(self, text: str, max_facts: int = 1000, max_rounds: int = 32):
        """Combine supported English facts and apply bounded symbolic inference."""
        extracted = self.extract_many(text)
        engine = IndependentReasoner(max_facts=max_facts, max_rounds=max_rounds)
        for item in extracted:
            for fact in item.facts:
                engine.add_fact(fact)
        engine.add_rule(Rule(
            "parent_from_father", (("father", "?x", "?y"),), ("parent", "?x", "?y")
        ))
        engine.add_rule(Rule(
            "parent_from_mother", (("mother", "?x", "?y"),), ("parent", "?x", "?y")
        ))
        engine.add_rule(Rule(
            "grandparent_transitive",
            (("parent", "?x", "?y"), ("parent", "?y", "?z")),
            ("grandparent", "?x", "?z"),
        ))
        return extracted, engine.infer()

    def reason(self, sentence: str, max_facts: int = 1000, max_rounds: int = 32):
        extracted = self.extract(sentence)
        engine = IndependentReasoner(max_facts=max_facts, max_rounds=max_rounds)
        for fact in extracted.facts:
            engine.add_fact(fact)
        if extracted.supported:
            engine.add_rule(Rule(
                "parent_from_father", (("father", "?x", "?y"),), ("parent", "?x", "?y")
            ))
            engine.add_rule(Rule(
                "parent_from_mother", (("mother", "?x", "?y"),), ("parent", "?x", "?y")
            ))
        return extracted, engine.infer()


def verbalize_fact(fact: Fact, language: str = "en") -> str:
    """Render supported relation facts using fixed English templates only."""
    if len(fact) != 3:
        raise ValueError("verbalizer expects a three-field relation fact")
    if language != "en":
        raise ValueError("language must be en")
    relation, subject, obj = fact
    labels = {
        "father": "is the father of",
        "mother": "is the mother of",
        "parent": "is a parent of",
        "friend": "is a friend of",
        "grandparent": "is the grandparent of",
    }
    if relation not in labels:
        raise ValueError("unsupported relation for English verbalization")
    return subject + " " + labels[relation] + " " + obj + "."
