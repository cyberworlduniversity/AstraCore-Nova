"""A deliberately limited, evidence-grounded agent shell."""
from __future__ import annotations
from dataclasses import dataclass
from .memory import EpisodicMemory

@dataclass(frozen=True)
class AgentReply:
    text: str
    evidence: tuple[str, ...]
    mode: str

class NovaAgent:
    def __init__(self, memory: EpisodicMemory | None = None, threshold: float = 0.90):
        if not -1.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between -1 and 1")
        self.memory = memory or EpisodicMemory()
        self.threshold = threshold

    def observe(self, text: str, tag: str = "knowledge") -> None:
        self.memory.remember(text, tag)

    def respond(self, query: str, learn: bool = False) -> AgentReply:
        if not isinstance(query, str) or not query.strip():
            return AgentReply("Please provide a non-empty input.", (), "validation")
        matches = self.memory.recall(query, limit=3)
        accepted = [(score, item) for score, item in matches if score >= self.threshold]
        if accepted:
            evidence = tuple(item.text for _, item in accepted)
            answer = "Related stored information (not independently verified):\n" + "\n".join(f"- {text}" for text in evidence)
            mode = "memory_retrieval"
        else:
            evidence = ()
            answer = ("I do not have sufficiently similar stored information to answer reliably. "
                      "This prototype does not yet perform general language understanding or generation.")
            mode = "unknown"
        if learn:
            self.memory.remember(query, "interaction")
        return AgentReply(answer, evidence, mode)
