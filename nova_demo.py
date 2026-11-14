from nova_core import NovaAgent

agent = NovaAgent()
agent.observe("வணக்கம் என்பது தமிழில் greeting ஆகும்.", "tamil")
agent.observe("Hello is a common English greeting.", "english")

for question in ("வணக்கம் என்பது தமிழில் greeting ஆகும்.", "What is an unknown topic?"):
    result = agent.respond(question)
    print(f"[{result.mode}] {result.text}")
