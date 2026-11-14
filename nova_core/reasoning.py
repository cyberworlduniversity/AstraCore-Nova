"""Deterministic symbolic inference over explicitly supplied atomic facts.

This is a bounded Horn-clause reasoner, not a natural-language parser or model.
Symbols are opaque Unicode strings: no tokenizer, token IDs, embeddings, or API.
"""
from __future__ import annotations
from dataclasses import dataclass

Fact = tuple[str, ...]
Substitution = dict[str, str]

@dataclass(frozen=True)
class Rule:
    name: str
    premises: tuple[Fact, ...]
    conclusion: Fact

    def __post_init__(self):
        if not self.name:
            raise ValueError("rule name must not be empty")
        if not self.premises:
            raise ValueError("rule must contain at least one premise")
        _validate_fact(self.conclusion)
        for premise in self.premises:
            _validate_fact(premise)

@dataclass(frozen=True)
class ProofStep:
    fact: Fact
    rule_name: str
    premises: tuple[Fact, ...]

@dataclass(frozen=True)
class ReasoningResult:
    facts: tuple[Fact, ...]
    derived: tuple[Fact, ...]
    proof: tuple[ProofStep, ...]
    rounds: int
    saturated: bool

def _validate_fact(fact: Fact) -> None:
    if not isinstance(fact, tuple) or not fact:
        raise ValueError("facts must be non-empty tuples")
    if not all(isinstance(item, str) and item for item in fact):
        raise ValueError("fact fields must be non-empty strings")

def _resolve(term: str, env: Substitution) -> str:
    seen = set()
    while term.startswith("?") and term in env and term not in seen:
        seen.add(term)
        term = env[term]
    return term

def _unify(pattern: Fact, fact: Fact, env: Substitution):
    if len(pattern) != len(fact):
        return None
    result = dict(env)
    for raw, value in zip(pattern, fact):
        term = _resolve(raw, result)
        if term.startswith("?"):
            existing = result.get(term)
            if existing is not None and _resolve(existing, result) != value:
                return None
            result[term] = value
        elif term != value:
            return None
    return result

def _instantiate(pattern: Fact, env: Substitution) -> Fact:
    return tuple(_resolve(term, env) for term in pattern)

class IndependentReasoner:
    """Deterministic, bounded forward-chaining positive-Horn reasoner."""
    def __init__(self, max_facts: int = 10000, max_rounds: int = 64):
        if max_facts < 1 or max_rounds < 1:
            raise ValueError("limits must be positive")
        self.max_facts = max_facts
        self.max_rounds = max_rounds
        self._facts = set()
        self._rules = []

    @property
    def facts(self):
        return tuple(sorted(self._facts))

    @property
    def rules(self):
        return tuple(self._rules)

    def add_fact(self, fact: Fact) -> None:
        _validate_fact(fact)
        if fact not in self._facts and len(self._facts) >= self.max_facts:
            raise RuntimeError("fact limit reached")
        self._facts.add(fact)

    def add_rule(self, rule: Rule) -> None:
        if not isinstance(rule, Rule):
            raise TypeError("rule must be a Rule")
        if any(old.name == rule.name for old in self._rules):
            raise ValueError("rule names must be unique")
        self._rules.append(rule)

    def query(self, pattern: Fact):
        _validate_fact(pattern)
        matches = []
        for fact in sorted(self._facts):
            env = _unify(pattern, fact, {})
            if env is not None:
                matches.append({key: _resolve(value, env)
                                for key, value in sorted(env.items())})
        return tuple(matches)

    def infer(self) -> ReasoningResult:
        proof_by_fact = {}
        rounds = 0
        saturated = False
        while rounds < self.max_rounds:
            rounds += 1
            additions = []
            current = tuple(sorted(self._facts))
            for rule in self._rules:
                environments = [({}, ())]
                for premise in rule.premises:
                    expanded = []
                    for env, used in environments:
                        for fact in current:
                            merged = _unify(premise, fact, env)
                            if merged is not None:
                                expanded.append((merged, used + (fact,)))
                    environments = expanded
                    if not environments:
                        break
                for env, used in environments:
                    conclusion = _instantiate(rule.conclusion, env)
                    if not any(term.startswith("?") for term in conclusion):
                        if conclusion not in self._facts:
                            additions.append(ProofStep(conclusion, rule.name, used))
            unique = {}
            for step in additions:
                unique.setdefault(step.fact, step)
            if not unique:
                saturated = True
                break
            if len(self._facts) + len(unique) > self.max_facts:
                raise RuntimeError("inference stopped: fact limit would be exceeded")
            for fact, step in sorted(unique.items()):
                self._facts.add(fact)
                proof_by_fact[fact] = step
        derived = tuple(sorted(proof_by_fact))
        return ReasoningResult(
            self.facts, derived,
            tuple(proof_by_fact[fact] for fact in derived),
            rounds, saturated,
        )
