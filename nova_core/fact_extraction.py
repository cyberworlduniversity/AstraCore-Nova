"""Transparent, bounded sentence-pattern extraction for Tamil and English.

This is not general NLP. It matches a small set of complete sentence forms.
No tokenization, model, embedding, or external API is used.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from .reasoning import Fact, IndependentReasoner, ReasoningResult, Rule

@dataclass(frozen=True)
class ExtractionResult:
    source: str
    facts: tuple[Fact, ...]
    language: str | None
    pattern: str | None
    supported: bool
    reason: str

class MultilingualFactExtractor:
    """Extract a narrow set of explicit family/friend relations."""
    _english = (
        ("english_parent", re.compile(r"^(?P<subject>.+?) is (?:a )?parent of (?P<object>.+?)$", re.I), "parent"),
        ("english_father", re.compile(r"^(?P<subject>.+?) is (?:the )?father of (?P<object>.+?)$", re.I), "father"),
        ("english_mother", re.compile(r"^(?P<subject>.+?) is (?:the )?mother of (?P<object>.+?)$", re.I), "mother"),
        ("english_friend", re.compile(r"^(?P<subject>.+?) is (?:a )?friend of (?P<object>.+?)$", re.I), "friend"),
    )
    _tamil = (
        ("tamil_father", re.compile(r"^(?P<subject>.+?)\s+(?P<object>.+?)(?:வின்|யின்|இன்)\s*(?P<relation>தந்தை)"), "father"),
        ("tamil_mother", re.compile(r"^(?P<subject>.+?)\s+(?P<object>.+?)(?:வின்|யின்|இன்)\s*(?P<relation>தாய்)"), "mother"),
        ("tamil_parent", re.compile(r"^(?P<subject>.+?)\s+(?P<object>.+?)(?:வின்|யின்|இன்)\s*(?P<relation>பெற்றோர்)"), "parent"),
    )

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"^[\s\u200b]+|[\s\u200b]+$", "", text).rstrip(".!?。！？")

    def extract(self, sentence: str) -> ExtractionResult:
        if not isinstance(sentence, str) or not sentence.strip():
            raise ValueError("sentence must be a non-empty string")
        text = self._clean(sentence)
        for name, pattern, relation in self._english:
            match = pattern.fullmatch(text)
            if match:
                subject = self._clean(match.group("subject"))
                obj = self._clean(match.group("object"))
                return self._result(sentence, (relation, subject, obj), "en", name)
        for name, pattern, relation in self._tamil:
            match = pattern.fullmatch(text)
            if match:
                subject = self._clean(match.group("subject"))
                obj = self._clean(match.group("object"))
                if subject and obj:
                    return self._result(sentence, (relation, subject, obj), "ta", name)
        return ExtractionResult(sentence, (), None, None, False,
                                "No supported sentence pattern matched; no facts inferred.")

    @staticmethod
    def _result(source: str, fact: Fact, language: str, pattern: str) -> ExtractionResult:
        return ExtractionResult(source, (fact,), language, pattern, True,
                                "Extracted by an explicit deterministic pattern.")

    def extract_many(self, text: str) -> tuple[ExtractionResult, ...]:\n        """Extract supported sentences split only on explicit sentence punctuation."""\n        if not isinstance(text, str) or not text.strip():\n            raise ValueError("text must be a non-empty string")\n        segments = [part.strip() for part in re.split(r"(?<=[.!?。！？])\\s+|(?<=[.!?。！？])(?=[\\u0b80-\\u0bffA-Za-z])", text) if part.strip()]\n        if not segments:\n            segments = [text.strip()]\n        return tuple(self.extract(part) for part in segments)\n\n    def reason_many(self, text: str, max_facts: int = 1000, max_rounds: int = 32):\n        """Extract multiple sentences, combine their facts, then infer across them."""\n        extracted = self.extract_many(text)\n        engine = IndependentReasoner(max_facts=max_facts, max_rounds=max_rounds)\n        for item in extracted:\n            for fact in item.facts:\n                engine.add_fact(fact)\n        engine.add_rule(Rule("parent_from_father", (("father", "?x", "?y"),),\n                             ("parent", "?x", "?y")))\n        engine.add_rule(Rule("parent_from_mother", (("mother", "?x", "?y"),),\n                             ("parent", "?x", "?y")))\n        engine.add_rule(Rule("grandparent_transitive", (\n            ("parent", "?x", "?y"), ("parent", "?y", "?z")\n        ), ("grandparent", "?x", "?z")))\n        return extracted, engine.infer()\n    def reason(self, sentence: str, max_facts: int = 1000, max_rounds: int = 32):
        extracted = self.extract(sentence)
        engine = IndependentReasoner(max_facts=max_facts, max_rounds=max_rounds)
        for fact in extracted.facts:
            engine.add_fact(fact)
        if extracted.supported:
            engine.add_rule(Rule("parent_from_father", (("father", "?x", "?y"),),
                                 ("parent", "?x", "?y")))
            engine.add_rule(Rule("parent_from_mother", (("mother", "?x", "?y"),),
                                 ("parent", "?x", "?y")))
        reasoning = engine.infer()
        return extracted, reasoning

def verbalize_fact(fact: Fact, language: str = "en") -> str:
    """Render supported relation facts using fixed, auditable templates."""
    if len(fact) != 3:
        raise ValueError("verbalizer expects a three-field relation fact")
    relation, subject, obj = fact
    if language == "ta":
        labels = {"father": "தந்தை", "mother": "தாய்", "parent": "பெற்றோர்", "friend": "நண்பர்"}
        if relation not in labels:
            raise ValueError("unsupported relation for Tamil verbalization")
        return subject + " — " + obj + "க்கு " + labels[relation] + "."
    if language == "en":
        labels = {"father": "is the father of", "mother": "is the mother of",
                  "parent": "is a parent of", "friend": "is a friend of"}
        if relation not in labels:
            raise ValueError("unsupported relation for English verbalization")
        return subject + " " + labels[relation] + " " + obj + "."
    raise ValueError("language must be en or ta")