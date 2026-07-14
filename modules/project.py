from core.prompts import build_system_prompt

def handle(topic, memory):
    try:
        from ollama import chat
    except ImportError as exc:
        raise RuntimeError("The ollama Python package is not installed. Install it with: pip install ollama") from exc

    response = chat(
        model=memory.get("settings", {}).get("model", "gemma2:2b"),
        messages=[
            {
                "role": "system",
                "content": build_system_prompt(memory, mode="""
Generate an innovative STEM project.

Include:
- Title
- Objective
- Materials
- Procedure
- Scientific Principle
- Applications
""")
            },
            {
                "role": "user",
                "content": topic
            }
        ]
    )

    return response["message"]["content"]
