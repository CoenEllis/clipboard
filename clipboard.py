import pyperclip
import json
import datetime
import threading
import time

from pynput import keyboard
from pynput.keyboard import Key, Controller

keyboard_controller = Controller()


class Clipboard:
    """
    The following code is for writing to the JSON:
    """
    # Constructor
    def __init__(
        self,
        filename: str = "clipboard.json",
        paste_keybind: str = "<ctrl>+<shift>",
    ):
        self.filename = filename
        self.content = self.load_content()
        self.last_text = pyperclip.paste()
        self.paste_keybind = paste_keybind
        self.disable = False

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

    """
    The following code is for the clipboard:
    """

    # Clipboard function
    def clipboard_function(self, delay=0.2):
        while True:
            try:
                text = pyperclip.paste()  # Get text from the clipboard
                if (
                    text != self.last_text
                    and text is not None
                    and not self.disable
                ):  # Checks if text is not empty and if enabled
                    self.last_text = text
                    self.add_content(text)
                time.sleep(delay)
            except Exception as e:
                print(f"Error in clipboard {e}")
                time.sleep(delay)

    # Start watching the clipboard
    def watch_clipboard(self):
        watcher_thread = threading.Thread(target=self.clipboard_function, daemon=True)
        watcher_thread.start()

    """
    The following code is for pasting:
    """

    # Function to paste from JSON
    def paste_from_history(self, index):
        history_index = -(index + 1)
        # This is to make sure there are enough items in history
        if len(self.content) >= (index + 1):
            content_paste = self.content[history_index]["content"]

            def do_paste():
                try:
                    self.disable = True
                    pyperclip.copy(content_paste)
                    while pyperclip.paste() != content_paste:
                        time.sleep(0.01)
                    keyboard_controller.press(Key.ctrl)
                    time.sleep(0.01)
                    keyboard_controller.press('v')
                    time.sleep(0.01)
                    keyboard_controller.release('v')
                    keyboard_controller.release(Key.ctrl)
                    # restore previous clipboard
                    pyperclip.copy(self.last_text)
                except Exception as e:
                    print(f"Error during paste thread: {e}")
                finally:
                    self.disable = False
            threading.Thread(target=do_paste, daemon=True).start()
        else:
            print("Index out of range")

    # Start watching the keyboard
    def watch_keyboard(self):
        hotkeys = {}
        for i in range(1, 11):  # Creates the hotkeys for the last 10 items copied
            key = f"{self.paste_keybind}+{i if i != 10 else 0}"
            hotkeys[key] = lambda i=i: self.paste_from_history(i)
        with keyboard.GlobalHotKeys(hotkeys) as h:
            h.join()


# Creates the object

clipboard = Clipboard()

if __name__ == "__main__":
    clipboard.watch_clipboard()
    clipboard.watch_keyboard()
