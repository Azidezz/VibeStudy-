from pathlib import Path

from core.assistant import ask_vibestudy
from core.memory import load_memory, save_memory
from core.pdf_reader import PdfReaderError, get_current_pdf, open_pdf, read_page
from core.profiles import (
    PROFILE_DEFINITIONS,
    get_active_profiles,
    profile_names,
    set_profile,
)
from core.tts import speak
from modules import career, project, research


BASE_DIR = Path(__file__).resolve().parent
MEMORY_FILE = BASE_DIR / "memory.json"


def print_and_speak(text, memory):
    print(text)
    if memory.get("settings", {}).get("tts"):
        ok, message = speak(text)
        if not ok:
            print(f"TTS unavailable: {message}")


def save(memory):
    save_memory(MEMORY_FILE, memory)


def show_help():
    profiles = ", ".join(profile_names())
    return f"""
VibeStudy commands:

/help
/settings
/profiles
/profile <name> on
/profile <name> off
/tts on
/tts off

/project <topic>
/research <topic>
/career <topic>

/pdf open <path>
/pdf read
/pdf read <page>
/pdf next
/pdf previous
/pdf summarize

remember <fact>
exit

Available profiles: {profiles}
""".strip()


def show_settings(memory):
    active = get_active_profiles(memory)
    active_text = ", ".join(active) if active else "none"
    tts = "on" if memory.get("settings", {}).get("tts") else "off"
    pdf = memory.get("pdf", {})
    current_pdf = pdf.get("current_file") or "none"
    return f"""
Current settings:
- Active profiles: {active_text}
- Text-to-speech: {tts}
- Current PDF: {current_pdf}
- PDF page: {pdf.get("current_page", 1)} of {pdf.get("page_count", 0)}
""".strip()


def show_profiles(memory):
    lines = ["Accessibility profiles:"]
    active = set(get_active_profiles(memory))
    for name, definition in PROFILE_DEFINITIONS.items():
        state = "on" if name in active else "off"
        lines.append(f"- {name}: {state} ({definition['label']})")
    return "\n".join(lines)


def handle_profile_command(q, memory):
    parts = q.split()
    if len(parts) != 3 or parts[2].lower() not in {"on", "off"}:
        return "Use: /profile <name> on or /profile <name> off"

    enabled = parts[2].lower() == "on"
    ok, normalized = set_profile(memory, parts[1], enabled)
    if not ok:
        return f"Unknown profile: {parts[1]}. Try /profiles."

    save(memory)
    state = "enabled" if enabled else "disabled"
    return f"{PROFILE_DEFINITIONS[normalized]['label']} {state}."


def handle_tts_command(q, memory):
    parts = q.split()
    if len(parts) != 2 or parts[1].lower() not in {"on", "off"}:
        return "Use: /tts on or /tts off"

    memory.setdefault("settings", {})["tts"] = parts[1].lower() == "on"
    save(memory)
    return f"Text-to-speech {'enabled' if memory['settings']['tts'] else 'disabled'}."


def handle_pdf_command(q, memory, history):
    parts = q.split(maxsplit=2)
    if len(parts) < 2:
        return "Use: /pdf open <path>, /pdf read <page>, /pdf next, /pdf previous, or /pdf summarize."

    action = parts[1].lower()

    if action == "open":
        if len(parts) < 3:
            return "Use: /pdf open <path>"
        pdf_state = open_pdf(parts[2].strip('"'))
        memory["pdf"] = pdf_state
        save(memory)
        return f"Opened PDF with {pdf_state['page_count']} pages. Current page is 1."

    current_file = get_current_pdf(memory)
    pdf_state = memory.setdefault("pdf", {})
    page_count = pdf_state.get("page_count", 0)
    current_page = pdf_state.get("current_page", 1)

    if action == "next":
        pdf_state["current_page"] = min(current_page + 1, page_count)
        save(memory)
        return read_page(current_file, pdf_state["current_page"])

    if action in {"previous", "prev", "back"}:
        pdf_state["current_page"] = max(current_page - 1, 1)
        save(memory)
        return read_page(current_file, pdf_state["current_page"])

    if action == "read":
        page = current_page
        if len(parts) == 3:
            page = int(parts[2])
            pdf_state["current_page"] = page
            save(memory)
        return read_page(current_file, page)

    if action == "summarize":
        page_text = read_page(current_file, current_page)
        return ask_vibestudy(
            f"Summarize this PDF page for studying:\n\n{page_text}",
            memory,
            history,
            mode="PDF study assistant",
        )

    return "Unknown PDF command. Try /help."


def main():
    memory = load_memory(MEMORY_FILE)
    history = []

    print("VibeStudy terminal ready. Type /help for commands.")

    while True:
        q = input("> ").strip()

        if not q:
            continue

        if q.lower() == "exit":
            break

        try:
            if q == "/help":
                print(show_help())
                continue

            if q == "/settings":
                print(show_settings(memory))
                continue

            if q == "/profiles":
                print(show_profiles(memory))
                continue

            if q.startswith("/profile "):
                print(handle_profile_command(q, memory))
                continue

            if q.startswith("/tts "):
                print(handle_tts_command(q, memory))
                continue

            if q.startswith("/pdf "):
                print_and_speak(handle_pdf_command(q, memory, history), memory)
                continue

            if q.startswith("/research "):
                print_and_speak(research.handle(q.replace("/research ", "", 1), memory), memory)
                continue

            if q.startswith("/project "):
                print_and_speak(project.handle(q.replace("/project ", "", 1), memory), memory)
                continue

            if q.startswith("/career "):
                print_and_speak(career.handle(q.replace("/career ", "", 1), memory), memory)
                continue

            if q.startswith("remember "):
                fact = q[9:].strip()
                if not fact:
                    print("Tell me what to remember after the word remember.")
                    continue
                memory.setdefault("facts", []).append(fact)
                save(memory)
                print("Saved.")
                continue

            reply = ask_vibestudy(q, memory, history)
            print_and_speak(reply, memory)

            history.append({"role": "user", "content": q})
            history.append({"role": "assistant", "content": reply})

        except PdfReaderError as error:
            print(f"PDF error: {error}")
        except ValueError:
            print("That page number was not valid.")
        except RuntimeError as error:
            print(f"Runtime error: {error}")
        except KeyboardInterrupt:
            print("\nUse exit to close VibeStudy.")


if __name__ == "__main__":
    main()
