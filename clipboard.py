import pyperclip
import json
import datetime
import threading
import time

class Clipboard:
    # Constructor
    def __init__(self, filename: str = "clipboard.json"):
        self.filename = filename
        self.content = self.load_content()
        self.last_text = pyperclip.paste()

    # Load content from JSON
    def load_content(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, IOError, OSError):
            return []

    # Save the new content to the JSON
    def save_content(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.content, f, indent=4)
        except (IOError, OSError) as e:
            print(f"Error saving content: {e}")

    # Add a new content to the JSON
    def add_content(self, content: str):
        timestamp = datetime.datetime.now()
        self.content.append({
            "content": content,
            "timestamp": timestamp.isoformat(),
        })
        self.save_content()

    def watch_clipboard(self, delay=0.2):
        while True:
            try:
                text = pyperclip.paste()
                if text != self.last_text:
                    self.last_text = text
                    self.add_content(text)
                time.sleep(delay)
            except Exception as e:
                print(f"Error in clipboard {e}")
                time.sleep(delay)

    # Start watching the clipboard
    def start_watching(self):
        watcher_thread = threading.Thread(target=self.watch_clipboard, daemon=True)
        watcher_thread.start()


clipboard = Clipboard()
if __name__ == "__main__":
    clipboard.start_watching()
    threading.Event().wait()
