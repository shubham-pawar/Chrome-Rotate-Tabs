import time
import chromedriver_autoinstaller
from selenium import webdriver
import threading
import tkinter as tk
from tkinter import messagebox
import os

# Always keep urls.txt next to this script, not in whatever folder the app was launched from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
URLS_FILE = os.path.join(BASE_DIR, "urls.txt")


class TabRotator:
    def __init__(self):
        self.urls = []
        self.interval = 10  # seconds
        self.driver = None
        self.stop_event = threading.Event()

    def start_browser(self):
        chromedriver_autoinstaller.install()
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

        if self.urls:
            self.driver.get(self.urls[0])
            for url in self.urls[1:]:
                if self.stop_event.is_set():
                    return
                self.driver.execute_script("window.open(arguments[0], '_blank');", url)
                self.stop_event.wait(1)

    def rotate_tabs(self):
        while not self.stop_event.is_set():
            for handle in list(self.driver.window_handles):
                if self.stop_event.is_set():
                    return
                self.driver.switch_to.window(handle)
                self.driver.refresh()
                # wait() returns immediately when Stop/Close is pressed, unlike time.sleep()
                if self.stop_event.wait(self.interval):
                    return

    def run(self):
        """Runs in the worker thread. The driver is created AND quit here, in the same thread."""
        self.stop_event.clear()
        try:
            self.start_browser()
            self.rotate_tabs()
        except Exception as e:
            print("Rotator stopped:", e)
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None

    def stop(self):
        # Just signal; the worker thread closes Chrome itself
        self.stop_event.set()


class UrlInputDialog:
    def __init__(self, parent, title="Add URL"):
        self.result = None

        self.top = tk.Toplevel(parent)
        self.top.title(title)
        # No fixed geometry: the window sizes itself to fit its contents at any DPI scaling
        self.top.resizable(True, False)
        self.top.transient(parent)

        tk.Label(self.top, text="Enter URL:", font=("Arial", 12)).pack(pady=(20, 10))

        self.entry = tk.Entry(self.top, width=60, font=("Arial", 12))
        self.entry.pack(padx=20, pady=10, fill="x")

        button_frame = tk.Frame(self.top)
        button_frame.pack(pady=15)

        tk.Button(button_frame, text="OK", width=12, command=self.ok).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", width=12, command=self.cancel).pack(side="left", padx=10)

        self.top.bind("<Return>", lambda event: self.ok())
        self.top.bind("<Escape>", lambda event: self.cancel())

        # Center on screen, and never larger than the screen
        self.top.update_idletasks()
        w = min(self.top.winfo_reqwidth(), self.top.winfo_screenwidth() - 40)
        h = min(self.top.winfo_reqheight(), self.top.winfo_screenheight() - 80)
        x = (self.top.winfo_screenwidth() - w) // 2
        y = (self.top.winfo_screenheight() - h) // 3
        self.top.geometry(f"{w}x{h}+{x}+{y}")

        self.top.grab_set()
        self.entry.focus_set()
        parent.wait_window(self.top)

    def ok(self):
        self.result = self.entry.get().strip()
        self.top.destroy()

    def cancel(self):
        self.top.destroy()


class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Tab Rotator")
        self.master.resizable(True, True)

        # Size the window relative to the screen instead of a fixed 720x960
        sw, sh = master.winfo_screenwidth(), master.winfo_screenheight()
        w, h = min(720, sw - 40), min(960, sh - 100)
        master.geometry(f"{w}x{h}+{(sw - w) // 2}+20")
        master.minsize(400, 350)

        self.tab_rotator = TabRotator()
        self.thread = None

        def style(bg, active):
            return {"font": ("Arial", 10, "bold"), "width": 20, "height": 2, "bg": bg,
                    "fg": "black", "activebackground": active, "activeforeground": "black"}

        # Pack the BUTTONS FIRST at the bottom so they always stay visible.
        # The listbox then gets whatever space is left over.
        button_frame = tk.Frame(master)
        button_frame.pack(side="bottom", fill="x", pady=10)
        button_frame.columnconfigure((0, 1), weight=1)

        self.start_button = tk.Button(button_frame, text="Start Rotating Tabs",
                                      command=self.start_rotation, **style("#A1FFA4", "#4dff00"))
        self.stop_button = tk.Button(button_frame, text="Stop",
                                     command=self.stop_rotation, **style("#FFA1A1", "#ff0000"))
        self.add_button = tk.Button(button_frame, text="Add URL",
                                    command=self.add_url, **style("#A1E0FF", "#0073ff"))
        self.remove_button = tk.Button(button_frame, text="Remove URL",
                                       command=self.remove_url, **style("#E7A1FF", "#ee00ff"))

        # 2x2 grid uses much less height than 4 stacked buttons
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
        self.add_button.grid(row=1, column=0, padx=5, pady=5)
        self.remove_button.grid(row=1, column=1, padx=5, pady=5)

        # Listbox with scrollbar fills the remaining space
        list_frame = tk.Frame(master)
        list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.url_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.url_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.url_listbox.yview)

        self.load_urls()
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_rotation(self):
        self.tab_rotator.urls = list(self.url_listbox.get(0, tk.END))
        if not self.tab_rotator.urls:
            messagebox.showwarning("No URLs", "Please add at least one URL.")
            return
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.tab_rotator.run, daemon=True)
            self.thread.start()

    def stop_rotation(self):
        # Don't join() here; that freezes the GUI. The worker thread closes Chrome itself.
        self.tab_rotator.stop()

    def add_url(self):
        dialog = UrlInputDialog(self.master, "Add URL")
        if dialog.result:
            self.url_listbox.insert(tk.END, dialog.result)

    def remove_url(self):
        selected = self.url_listbox.curselection()
        if selected:
            self.url_listbox.delete(selected[0])

    def on_close(self):
        # Ask first, so Cancel doesn't stop the rotation
        if not messagebox.askokcancel("Quit", "Do you really want to quit?"):
            return
        try:
            self.save_urls()
        except Exception as e:
            print("Could not save URLs:", e)
        self.stop_rotation()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)  # give Chrome a moment to close, but never hang
        self.master.destroy()

    def save_urls(self):
        with open(URLS_FILE, "w", encoding="utf-8") as f:
            for url in self.url_listbox.get(0, tk.END):
                f.write(url + "\n")

    def load_urls(self):
        if os.path.exists(URLS_FILE):
            with open(URLS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self.url_listbox.insert(tk.END, line.strip())


if __name__ == "__main__":
    # Make Tkinter DPI-aware on Windows so layout/scaling is correct on TVs and 4K screens
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    app = App(root)
    root.mainloop()