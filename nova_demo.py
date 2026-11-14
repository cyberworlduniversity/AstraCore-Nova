"""English-only end-to-end AstraCore Nova demonstration."""
from nova_core import EnglishKnowledgeEngine, verbalize_fact

engine = EnglishKnowledgeEngine()
result = engine.process("Arun is the father of Maya. Maya is the mother of Ravi.", source="demo-knowledge-base")

print("Extracted facts:")
for item in result.extraction:
    for fact in item.facts:
        print(" -", verbalize_fact(fact))

print("\nDerived facts:")
for fact in result.reasoning.derived:
    try:
        print(" -", verbalize_fact(fact))
    except ValueError:
        print(" -", fact)

print("\nEvidence records:", len(result.memory.facts))
print("Contradictions:", len(result.memory.conflicts))
