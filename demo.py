from nova_field import NovaFieldMemory

memory = NovaFieldMemory(capacity=32)
memory.store("tamil-greeting", "வணக்கம்")
memory.store("english-greeting", "hello")
memory.store("coding", "write a Python function")

for score, record in memory.recall("வணக்கம்"):
    print(f"{score:.4f}  {record.label}: {record.content}")
