"""English-only NFD field memory demonstration."""
from nova_field import NovaFieldMemory

memory = NovaFieldMemory(capacity=32)
memory.store("english-greeting", "Hello is a common English greeting.")
memory.store("coding", "Write a Python function to sort a list.")
memory.store("security", "Use multi-factor authentication to protect accounts.")

for score, record in memory.recall("Hello is a common English greeting.")[:3]:
    print(f"{score:.4f}  {record.label}: {record.content}")
