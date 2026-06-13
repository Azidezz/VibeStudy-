from ollama import chat

def handle(topic, memory):

    response = chat(
        model="vibestudy:latest",
        messages=[
            {
                "role": "system",
                "content": f"""
You are VibeStudy.

User Memory:
{memory}

Act as a STEM research assistant.

Provide:
- Overview
- Key Concepts
- Current Research
- Applications
- Future Directions
"""
            },
            {
                "role": "user",
                "content": topic
            }
        ]
    )

    return response["message"]["content"]
