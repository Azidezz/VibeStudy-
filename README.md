# VibeStudy

AI-Powered STEM Research & Learning Assistant

VibeStudy is an educational AI assistant designed to help students with STEM research, project ideation, career exploration, and accessible learning.

## Features

- STEM Project Generation
- Research Assistance
- Career Guidance
- Persistent User Memory
- Personalized Learning Support
- Accessibility-Oriented Design
- AMOLED desktop/mobile-style GUI

## Terminal Commands

```text
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
```

## GUI

Run the cross-platform Kivy interface from the project folder:

```bash
python gui.py
```

The GUI uses the same local project contents as the terminal app:

- `memory.json`
- `core/`
- `modules/`
- local Ollama model setting
- PDF reader and text-to-speech helpers

The interface is built with Kivy so it can run on PC now and be packaged for Android later with a Kivy Android workflow such as Buildozer.

## Accessibility

VibeStudy is being developed with accessibility in mind.

Current profiles include:

- ADHD support
- Autism support
- Dyslexia support
- Mobility support
- Simple language
- Low vision support

These profiles can be combined so the learner is supported by need, not boxed into one label.

Accessibility features include:

- Local text-to-speech toggle
- PDF open/read/next/previous/summarize commands
- Screen-reader-friendly response shaping
- Memory-backed accessibility preferences
- Touch-friendly AMOLED GUI controls

## Installation

```bash
git clone https://github.com/Azidezz/VibeStudy.git

cd VibeStudy

pip install -r requirements.txt

./install.sh
```

## Roadmap

- [x] Memory System
- [x] Research Mode
- [x] Career Mode
- [x] STEM Project Generator
- [x] Accessibility Preferences
- [x] PDF Research Summaries
- [x] Local Text-to-Speech Toggle
- [x] GUI Version
- [ ] Android packaging workflow
- [ ] Head/tilt navigation
- [ ] YouTube Video Summaries
- [ ] Web Research Integration
- [ ] OpenDyslexic Support in GUI

## Status

This project is currently under active development.

Features and APIs may change as VibeStudy evolves.
