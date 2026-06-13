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

Generate an innovative STEM project.

Include:
- Title
- Objective
- Materials
- Procedure
- Scientific Principle
- Applications
"""
            },
            {
                "role": "user",
                "content": topic
            }
        ]
    )

    return response["message"]["content"]
