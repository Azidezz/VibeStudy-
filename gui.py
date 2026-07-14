import os
from pathlib import Path
from threading import Thread

BASE_DIR = Path(__file__).resolve().parent
os.environ.setdefault("KIVY_HOME", str(BASE_DIR / ".kivy"))

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from core.assistant import ask_vibestudy
from core.memory import load_memory, save_memory
from core.pdf_reader import PdfReaderError, get_current_pdf, open_pdf, read_page
from core.profiles import PROFILE_DEFINITIONS, get_active_profiles, set_profile
from core.tts import speak
from modules import career, project, research


BASE_DIR = Path(__file__).resolve().parent
MEMORY_FILE = BASE_DIR / "memory.json"

COLORS = {
    "bg": (0.0, 0.0, 0.018, 1),
    "panel": (0.018, 0.022, 0.04, 1),
    "panel_soft": (0.035, 0.042, 0.072, 1),
    "accent": (0.22, 0.96, 0.82, 1),
    "accent_dim": (0.045, 0.18, 0.17, 1),
    "text": (0.9, 0.95, 0.98, 1),
    "muted": (0.56, 0.64, 0.7, 1),
    "user": (0.06, 0.14, 0.16, 1),
    "assistant": (0.025, 0.03, 0.055, 1),
}


class Surface(BoxLayout):
    def __init__(self, bg="panel", radius=8, **kwargs):
        super().__init__(**kwargs)
        self._radius = dp(radius)
        with self.canvas.before:
            Color(*COLORS[bg])
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])
        self.bind(pos=self._sync_rect, size=self._sync_rect)

    def _sync_rect(self, *_args):
        self._rect.pos = self.pos
        self._rect.size = self.size


class VibeButton(Button):
    active = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.font_size = dp(13)
        self.color = COLORS["text"]
        self.size_hint_y = None
        self.height = dp(42)
        self.padding = (dp(10), dp(8))
        self.bind(active=self._paint, state=self._paint)
        self._paint()

    def _paint(self, *_args):
        if self.active or self.state == "down":
            self.background_color = COLORS["accent_dim"]
            self.color = COLORS["accent"]
        else:
            self.background_color = COLORS["panel_soft"]
            self.color = COLORS["text"]


class ChatBubble(Label):
    def __init__(self, text, author="assistant", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.color = COLORS["text"] if author == "assistant" else (0.84, 1, 0.95, 1)
        self.font_size = dp(16)
        self.padding = (dp(14), dp(12))
        self.size_hint_y = None
        self.halign = "left"
        self.valign = "top"
        self.text_size = (max(Window.width - dp(44), dp(260)), None)
        self.bind(texture_size=self._resize)
        with self.canvas.before:
            Color(*(COLORS["assistant"] if author == "assistant" else COLORS["user"]))
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        self.bind(pos=self._sync_rect, size=self._sync_rect)
        Window.bind(size=self._window_resize)

    def _resize(self, *_args):
        self.height = self.texture_size[1] + dp(24)

    def _sync_rect(self, *_args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def _window_resize(self, *_args):
        self.text_size = (max(Window.width - dp(44), dp(260)), None)


class VibeStudyGui(App):
    title = "VibeStudy"

    def build(self):
        Window.clearcolor = COLORS["bg"]
        self.memory = load_memory(MEMORY_FILE)
        self.history = []
        self.busy = False
        self.mode = None
        self.profile_buttons = {}
        self.mode_buttons = {}

        root = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        header = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(70), spacing=dp(2))
        title = Label(
            text="VibeStudy",
            color=COLORS["text"],
            font_size=dp(28),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(38),
            text_size=(Window.width, dp(38)),
        )
        subtitle = Label(
            text="local STEM assistant with adaptive accessibility profiles",
            color=COLORS["muted"],
            font_size=dp(13),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(24),
            text_size=(Window.width, dp(24)),
        )
        header.add_widget(title)
        header.add_widget(subtitle)
        root.add_widget(header)

        profile_bar = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        for name, definition in PROFILE_DEFINITIONS.items():
            label = definition["label"].replace(" support", "")
            button = VibeButton(text=label)
            button.bind(on_release=lambda _instance, profile=name: self.toggle_profile(profile))
            self.profile_buttons[name] = button
            profile_bar.add_widget(button)
        root.add_widget(profile_bar)

        tools = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        for label, mode in [("Chat", None), ("Research", "research"), ("Project", "project"), ("Career", "career")]:
            button = VibeButton(text=label)
            button.bind(on_release=lambda _instance, selected=mode: self.set_mode(selected))
            self.mode_buttons[mode or "chat"] = button
            tools.add_widget(button)
        self.tts_button = VibeButton(text="TTS")
        self.tts_button.bind(on_release=lambda _instance: self.toggle_tts())
        tools.add_widget(self.tts_button)
        root.add_widget(tools)

        pdf_tools = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        for label, action in [
            ("Open PDF", self.open_pdf_popup),
            ("Prev", lambda: self.pdf_action("previous")),
            ("Read", lambda: self.pdf_action("read")),
            ("Next", lambda: self.pdf_action("next")),
            ("Summarize", lambda: self.pdf_action("summarize")),
        ]:
            button = VibeButton(text=label)
            button.bind(on_release=lambda _instance, callback=action: callback())
            pdf_tools.add_widget(button)
        root.add_widget(pdf_tools)

        self.scroll = ScrollView(do_scroll_x=False)
        self.chat_log = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=(0, 0, 0, dp(4)))
        self.chat_log.bind(minimum_height=self.chat_log.setter("height"))
        self.scroll.add_widget(self.chat_log)
        root.add_widget(self.scroll)

        composer = Surface(orientation="horizontal", bg="panel", size_hint_y=None, height=dp(64), padding=dp(8), spacing=dp(8))
        self.input = TextInput(
            hint_text="Ask VibeStudy...",
            multiline=False,
            background_normal="",
            background_active="",
            background_color=(0.012, 0.016, 0.028, 1),
            foreground_color=COLORS["text"],
            cursor_color=COLORS["accent"],
            hint_text_color=COLORS["muted"],
            font_size=dp(16),
            padding=(dp(12), dp(14)),
        )
        self.input.bind(on_text_validate=lambda _instance: self.send_message())
        send = VibeButton(text="Send", size_hint_x=None, width=dp(86))
        send.bind(on_release=lambda _instance: self.send_message())
        composer.add_widget(self.input)
        composer.add_widget(send)
        root.add_widget(composer)

        self.refresh_state()
        self.add_message("VibeStudy GUI ready. Pick profiles above, choose a mode, or open a PDF.", "assistant")
        return root

    def save(self):
        save_memory(MEMORY_FILE, self.memory)

    def refresh_state(self):
        active = set(get_active_profiles(self.memory))
        for name, button in self.profile_buttons.items():
            button.active = name in active
        for key, button in self.mode_buttons.items():
            button.active = (self.mode or "chat") == key
        self.tts_button.active = bool(self.memory.get("settings", {}).get("tts"))

    def add_message(self, text, author="assistant"):
        self.chat_log.add_widget(ChatBubble(text=text, author=author))
        Clock.schedule_once(lambda _dt: setattr(self.scroll, "scroll_y", 0), 0.05)

    def set_mode(self, mode):
        self.mode = mode
        self.refresh_state()
        self.add_message(f"Mode set to {mode or 'chat'}.", "assistant")

    def toggle_profile(self, profile):
        enabled = profile not in get_active_profiles(self.memory)
        ok, normalized = set_profile(self.memory, profile, enabled)
        if ok:
            self.save()
            state = "on" if enabled else "off"
            self.refresh_state()
            self.add_message(f"{PROFILE_DEFINITIONS[normalized]['label']} is {state}.", "assistant")

    def toggle_tts(self):
        settings = self.memory.setdefault("settings", {})
        settings["tts"] = not bool(settings.get("tts"))
        self.save()
        self.refresh_state()
        self.add_message(f"Text-to-speech is {'on' if settings['tts'] else 'off'}.", "assistant")

    def send_message(self):
        text = self.input.text.strip()
        if not text or self.busy:
            return
        self.input.text = ""
        self.add_message(text, "user")
        self.run_async(lambda: self.process_message(text))

    def process_message(self, text):
        if self.mode == "research":
            return research.handle(text, self.memory)
        if self.mode == "project":
            return project.handle(text, self.memory)
        if self.mode == "career":
            return career.handle(text, self.memory)

        reply = ask_vibestudy(text, self.memory, self.history)
        self.history.append({"role": "user", "content": text})
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def run_async(self, work):
        self.busy = True
        self.add_message("Thinking...", "assistant")

        def target():
            try:
                reply = work()
            except Exception as error:
                reply = f"Error: {error}"
            Clock.schedule_once(lambda _dt: self.finish_async(reply), 0)

        Thread(target=target, daemon=True).start()

    def finish_async(self, reply):
        self.busy = False
        if self.chat_log.children:
            newest = self.chat_log.children[0]
            if isinstance(newest, ChatBubble) and newest.text == "Thinking...":
                self.chat_log.remove_widget(newest)
        self.add_message(reply, "assistant")
        if self.memory.get("settings", {}).get("tts"):
            Thread(target=lambda: speak(reply), daemon=True).start()

    def open_pdf_popup(self):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(10))
        path_input = TextInput(
            hint_text="Paste PDF path",
            multiline=False,
            background_normal="",
            background_active="",
            background_color=(0.012, 0.016, 0.028, 1),
            foreground_color=COLORS["text"],
            cursor_color=COLORS["accent"],
            hint_text_color=COLORS["muted"],
        )
        actions = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        popup = Popup(title="Open PDF", content=content, size_hint=(0.92, 0.35))
        open_button = VibeButton(text="Open")
        cancel_button = VibeButton(text="Cancel")
        open_button.bind(on_release=lambda _instance: self.load_pdf_from_popup(path_input.text, popup))
        cancel_button.bind(on_release=lambda _instance: popup.dismiss())
        actions.add_widget(cancel_button)
        actions.add_widget(open_button)
        content.add_widget(path_input)
        content.add_widget(actions)
        popup.open()

    def load_pdf_from_popup(self, path, popup):
        try:
            self.memory["pdf"] = open_pdf(path.strip().strip('"'))
            self.save()
            popup.dismiss()
            self.add_message(f"Opened PDF with {self.memory['pdf']['page_count']} pages.", "assistant")
        except PdfReaderError as error:
            self.add_message(f"PDF error: {error}", "assistant")

    def pdf_action(self, action):
        if self.busy:
            return
        self.run_async(lambda: self.process_pdf_action(action))

    def process_pdf_action(self, action):
        current_file = get_current_pdf(self.memory)
        pdf_state = self.memory.setdefault("pdf", {})
        page_count = pdf_state.get("page_count", 0)
        current_page = pdf_state.get("current_page", 1)

        if action == "next":
            pdf_state["current_page"] = min(current_page + 1, page_count)
        elif action == "previous":
            pdf_state["current_page"] = max(current_page - 1, 1)

        self.save()
        page_text = read_page(current_file, pdf_state.get("current_page", 1))

        if action == "summarize":
            return ask_vibestudy(
                f"Summarize this PDF page for studying:\n\n{page_text}",
                self.memory,
                self.history,
                mode="PDF study assistant",
            )
        return page_text


if __name__ == "__main__":
    VibeStudyGui().run()

