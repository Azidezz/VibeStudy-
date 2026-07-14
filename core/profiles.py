PROFILE_DEFINITIONS = {
    "adhd": {
        "label": "ADHD support",
        "instructions": [
            "Keep answers focused and avoid long setup.",
            "Use short sections with clear labels.",
            "Give one next action at the end.",
            "Break tasks into small steps.",
            "Use brief check-ins when a task has many stages.",
        ],
    },
    "autism": {
        "label": "Autism support",
        "instructions": [
            "Use literal, precise language.",
            "Avoid sarcasm, vague hints, and unexplained idioms.",
            "Make expectations and assumptions explicit.",
            "Use predictable structure.",
            "Flag changes in topic before moving on.",
        ],
    },
    "dyslexia": {
        "label": "Dyslexia support",
        "instructions": [
            "Use short paragraphs.",
            "Prefer bullet points for lists.",
            "Avoid dense walls of text.",
            "Use plain formatting and clear headings.",
            "Keep line length comfortable.",
        ],
    },
    "mobility": {
        "label": "Mobility support",
        "instructions": [
            "Minimize required typing.",
            "Offer numbered options when choices are useful.",
            "Keep commands simple and voice-friendly.",
            "Avoid asking the learner to repeat information.",
            "Support next, back, read, pause, and repeat style navigation.",
        ],
    },
    "simple": {
        "label": "Simple language",
        "instructions": [
            "Use simple words unless the learner asks for technical terms.",
            "Explain one idea at a time.",
            "Define important terms briefly.",
            "Use examples before abstractions.",
        ],
    },
    "low_vision": {
        "label": "Low vision support",
        "instructions": [
            "Make answers screen-reader friendly.",
            "Avoid relying on tables for important information.",
            "Describe visual information in words.",
            "Use clear labels for steps and choices.",
        ],
    },
}

ALIASES = {
    "autistic": "autism",
    "autistic_child": "autism",
    "autistic-child": "autism",
    "adhd_child": "adhd",
    "adhd-child": "adhd",
    "dyslexic": "dyslexia",
    "limb": "mobility",
    "limb_disability": "mobility",
    "physical": "mobility",
    "easy": "simple",
}


def normalize_profile_name(name):
    key = name.strip().lower().replace(" ", "_")
    return ALIASES.get(key, key)


def profile_names():
    return sorted(PROFILE_DEFINITIONS.keys())


def get_active_profiles(memory):
    profiles = memory.get("accessibility", {}).get("profiles", {})
    return [name for name, enabled in profiles.items() if enabled]


def set_profile(memory, name, enabled):
    normalized = normalize_profile_name(name)
    if normalized not in PROFILE_DEFINITIONS:
        return False, normalized

    memory.setdefault("accessibility", {}).setdefault("profiles", {})
    memory["accessibility"]["profiles"][normalized] = enabled
    return True, normalized


def build_accessibility_instructions(memory):
    active = get_active_profiles(memory)
    if not active:
        return "No accessibility profile is currently enabled."

    lines = ["Accessibility profiles currently enabled:"]
    for name in active:
        definition = PROFILE_DEFINITIONS.get(name)
        if not definition:
            continue
        lines.append(f"\n{name}: {definition['label']}")
        for instruction in definition["instructions"]:
            lines.append(f"- {instruction}")

    lines.extend(
        [
            "\nAlways adapt the response to these supports without making the learner feel singled out.",
            "Do not diagnose the learner or claim that a profile proves any medical condition.",
            "If safety, health, abuse, self-harm, or urgent wellbeing comes up, advise involving a trusted adult or professional.",
        ]
    )
    return "\n".join(lines)
