from core.prompts import build_system_prompt


def ask_vibestudy(user_text, memory, history=None, mode=None):
    try:
        from ollama import chat
    except ImportError as exc:
        raise RuntimeError("The ollama Python package is not installed. Install it with: pip install ollama") from exc

    model = memory.get("settings", {}).get("model", "gemma2:2b")
    messages = [{"role": "system", "content": build_system_prompt(memory, mode=mode)}]

    if history:
        messages.extend(history[-10:])

    messages.append({"role": "user", "content": user_text})

    response = chat(model=model, messages=messages)
    return response["message"]["content"]
