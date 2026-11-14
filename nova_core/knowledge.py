"""End-to-end English fact extraction, memory, and bounded inference."""
from __future__ import annotations
from dataclasses import dataclass
from .fact_extraction import EnglishFactExtractor, ExtractionResult
from .fact_memory import FactMemory, MemoryReport
from .reasoning import IndependentReasoner, ReasoningResult, Rule

@dataclass(frozen=True)
class KnowledgeResult:
    extraction: tuple[ExtractionResult, ...]
    reasoning: ReasoningResult
    memory: MemoryReport

class EnglishKnowledgeEngine:
    """Connect supported English patterns to provenance memory and inference."""
    def __init__(self, capacity: int = 1000, max_rounds: int = 32,
                 contradiction_pairs=()):
        if not isinstance(max_rounds, int) or max_rounds < 1:
            raise ValueError("max_rounds must be a positive integer")
        self.extractor = EnglishFactExtractor()
        self.memory = FactMemory(
            capacity=capacity, contradiction_pairs=contradiction_pairs
        )
        self.max_rounds = max_rounds

    @staticmethod
    def _rules():
        return (
            Rule("parent_from_father", (("father", "?x", "?y"),),
                 ("parent", "?x", "?y")),
            Rule("parent_from_mother", (("mother", "?x", "?y"),),
                 ("parent", "?x", "?y")),
            Rule("grandparent_transitive", (
                ("parent", "?x", "?y"), ("parent", "?y", "?z")
            ), ("grandparent", "?x", "?z")),
        )

    def process(self, text: str, source: str = "user_input") -> KnowledgeResult:
        if not isinstance(source, str) or not source.strip():
            raise ValueError("source must be a non-empty string")
        source = source.strip()
        extracted = self.extractor.extract_many(text)
        for item in extracted:
            for fact in item.facts:
                self.memory.add(fact, source)
        reasoner = IndependentReasoner(
            max_facts=max(1, self.memory.capacity), max_rounds=self.max_rounds
        )
        for record in self.memory.facts:
            reasoner.add_fact(record.fact)
        for rule in self._rules():
            reasoner.add_rule(rule)
        reasoning = reasoner.infer()
        for step in reasoning.proof:
            self.memory.add(step.fact, "inference:" + step.rule_name)
        return KnowledgeResult(extracted, reasoning, self.memory.report())
