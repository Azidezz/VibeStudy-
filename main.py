import json
from ollama import chat
from modules import research
from modules import project
from modules import career

MEMORY_FILE = "memory.json"

with open(MEMORY_FILE, "r") as f:
    memory = json.load(f)

messages = []
while True:
    q = input("> ")

    if q.lower() == "exit":
        break

    if q.startswith("/research "):
        topic = q.replace("/research ", "")

        print(research.handle(topic, memory))
        continue

    if q.startswith("/project "):
        topic = q.replace("/project ", "")

        print(project.handle(topic, memory))
        continue

    if q.startswith("/career "):
        topic = q.replace("/career ", "")

        print(career.handle(topic, memory))
        continue

    if q == "/dyslexia on":
        memory["accessibility"]["dyslexia_mode"] = True

        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=4)

        print("Dyslexia mode enabled.")
        continue

    if q == "/dyslexia off":
        memory["accessibility"]["dyslexia_mode"] = False

        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=4)

        print("Dyslexia mode disabled.")
        continue

    if q == "/simple on":
        memory["accessibility"]["simple_language"] = True

        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=4)

        print("Simple language enabled.")
        continue

    if q == "/simple off":
        memory["accessibility"]["simple_language"] = False

        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=4)

        print("Simple language disabled.")
        continue

    if q.startswith("remember "):
        fact = q[9:]

        memory["facts"].append(fact)

        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=4)

        print("Saved.")
        continue

    system_prompt = f"""
You are VibeStudy.

User Memory:
{memory}

If dyslexia_mode is enabled:
- Use short paragraphs
- Use bullet points
- Avoid walls of text
- Use clear formatting

If simple_language is enabled:
- Explain concepts using simple words
- Avoid technical jargon unless requested
- Break information into steps
"""
    msgs = [
    {
        "role": "system",
        "content": system_prompt
    }
]

msgs.extend(messages[-10:])

msgs.append({
    "role": "user",
    "content": q
})

response = chat(
    model="gemma2:2b",
    messages=msgs
)

reply = response["message"]["content"]

print(reply)

messages.append({
    "role": "user",
    "content": q
})

messages.append({
    "role": "assistant",
    "content": reply
})
