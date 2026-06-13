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

Act as a STEM career advisor.

Provide:
- Required Skills
- Education Path
- Opportunities
- Salary Outlook
- Future Demand
"""
            },
            {
                "role": "user",
                "content": topic
            }
        ]
    )

    return response["message"]["content"]
