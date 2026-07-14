import platform
import shutil
import subprocess


def speak(text):
    if not text.strip():
        return False, "Nothing to speak."

    try:
        from plyer import tts

        tts.speak(text)
        return True, "Spoken with mobile text-to-speech."
    except Exception:
        pass

    system = platform.system().lower()

    if system == "windows":
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                "Add-Type -AssemblyName System.Speech; "
                "$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$speaker.Rate = 0; "
                "$speaker.Speak([Console]::In.ReadToEnd())"
            ),
        ]
        subprocess.run(command, input=text, text=True, check=False)
        return True, "Spoken with Windows text-to-speech."

    if shutil.which("say"):
        subprocess.run(["say", text], check=False)
        return True, "Spoken with system text-to-speech."

    if shutil.which("espeak"):
        subprocess.run(["espeak", text], check=False)
        return True, "Spoken with eSpeak."

    return False, "No local text-to-speech engine was found."
