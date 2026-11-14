"""Transparent, bounded English sentence-pattern fact extraction.

This is deterministic pattern matching, not general NLP. It matches complete,
documented English forms and emits explicit relation tuples. No tokenizer,
token IDs, language model, embeddings, or external API are used.
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
    """Extract explicit English relations using a bounded grammar catalogue."""

    # Order is deliberate: more specific forms precede broader forms.
    _patterns = (
        ("english_father", re.compile(
            r"^(?P<subject>.+?) is (?:the )?father of (?P<object>.+?)$", re.I
        ), "father"),
        ("english_mother", re.compile(
            r"^(?P<subject>.+?) is (?:the )?mother of (?P<object>.+?)$", re.I
        ), "mother"),
        ("english_parent", re.compile(
            r"^(?P<subject>.+?) is (?:a )?parent of (?P<object>.+?)$", re.I
        ), "parent"),
        ("english_friend", re.compile(
            r"^(?P<subject>.+?) is (?:a )?friend of (?P<object>.+?)$", re.I
        ), "friend"),
        ("english_spouse", re.compile(
            r"^(?P<subject>.+?) is married to (?P<object>.+?)$", re.I
        ), "spouse"),
        ("english_resides", re.compile(
            r"^(?P<subject>.+?) (?:lives|resides) in (?P<object>.+?)$", re.I
        ), "lives_in"),
        ("english_located", re.compile(
            r"^(?P<subject>.+?) is located in (?P<object>.+?)$", re.I
        ), "lives_in"),
        ("english_employment", re.compile(
            r"^(?P<subject>.+?) (?:works|is employed) at (?P<object>.+?)$", re.I
        ), "works_at"),
        ("english_knowledge", re.compile(
            r"^(?P<subject>.+?) knows (?P<object>.+?)$", re.I
        ), "knows"),
        ("english_ownership", re.compile(
            r"^(?P<subject>.+?) owns (?P<object>.+?)$", re.I
        ), "owns"),
        ("english_preference_like", re.compile(
            r"^(?P<subject>.+?) likes (?P<object>.+?)$", re.I
        ), "likes"),
        ("english_preference_love", re.compile(
            r"^(?P<subject>.+?) loves (?P<object>.+?)$", re.I
        ), "loves"),
    )

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"^[\s\u200b]+|[\s\u200b]+$", "", text).rstrip(".!?").strip()

    def extract(self, sentence: str) -> ExtractionResult:
        if not isinstance(sentence, str) or not sentence.strip():
            raise ValueError("sentence must be a non-empty string")
        text = self._clean(sentence)
        for name, pattern, relation in self._patterns:
            match = pattern.fullmatch(text)
            if match:
                subject = self._clean(match.group("subject"))
                obj = self._clean(match.group("object"))
                uncertain_prefixes = ("i think ", "i believe ", "perhaps ", "maybe ", "probably ")
                if (
                    subject
                    and obj
                    and subject.casefold() != obj.casefold()
                    and not subject.casefold().startswith(uncertain_prefixes)
                ):
                    return ExtractionResult(
                        sentence, ((relation, subject, obj),), "en", name, True,
                        "Extracted by an explicit deterministic English pattern.",
                    )
        return ExtractionResult(
            sentence, (), None, None, False,
            "No supported English sentence pattern matched; no facts inferred.",
        )

    def extract_many(self, text: str) -> tuple[ExtractionResult, ...]:
        """Split on sentence-final punctuation followed by whitespace."""
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
        """Extract facts and apply bounded positive-Horn family inference."""
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
        if extracted.supported and extracted.facts[0][0] in {"father", "mother"}:
            relation = extracted.facts[0][0]
            engine.add_rule(Rule(
                "parent_from_" + relation,
                ((relation, "?x", "?y"),), ("parent", "?x", "?y")
            ))
        return extracted, engine.infer()


def verbalize_fact(fact: Fact, language: str = "en") -> str:
    """Render known relation facts using fixed English templates only."""
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
        "spouse": "is married to",
        "lives_in": "lives in",
        "works_at": "works at",
        "knows": "knows",
        "owns": "owns",
        "likes": "likes",
        "loves": "loves",
    }
    if relation not in labels:
        raise ValueError("unsupported relation for English verbalization")
    return subject + " " + labels[relation] + " " + obj + "."
