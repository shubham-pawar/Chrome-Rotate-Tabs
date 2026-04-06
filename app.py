import time
import chromedriver_autoinstaller
from selenium import webdriver
import threading
import tkinter as tk
from tkinter import messagebox
import os


class TabRotator:
    def __init__(self):
        self.urls = []
        self.interval = 10  # seconds
        self.driver = None
        self.running = False

    def start_browser(self):
        chromedriver_autoinstaller.install()
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

        if self.urls:
            self.driver.get(self.urls[0])
            time.sleep(1)

            for url in self.urls[1:]:
                self.driver.execute_script("window.open(arguments[0], '_blank');", url)
                time.sleep(1)

    def rotate_tabs(self):
        while self.running:
            for index in range(len(self.driver.window_handles)):
                if not self.running:
                    break
                self.driver.switch_to.window(self.driver.window_handles[index])
                self.driver.refresh()
                time.sleep(self.interval)

    def run(self):
        self.running = True
        self.start_browser()
        self.rotate_tabs()

    def stop(self):
        self.running = False
        if self.driver:
            self.driver.quit()
            self.driver = None


class UrlInputDialog:
    def __init__(self, parent, title="Add URL"):
        self.result = None

        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("500x180")   # popup window size
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()

        tk.Label(self.top, text="Enter URL:", font=("Arial", 12)).pack(pady=(20, 10))

        self.entry = tk.Entry(self.top, width=60, font=("Arial", 12))  # bigger field
        self.entry.pack(padx=20, pady=10, fill="x")
        self.entry.focus_set()

        button_frame = tk.Frame(self.top)
        button_frame.pack(pady=15)

        tk.Button(button_frame, text="OK", width=12, command=self.ok).pack(side="left", padx=10)
        tk.Button(button_frame, text="Cancel", width=12, command=self.cancel).pack(side="left", padx=10)

        self.top.bind("<Return>", lambda event: self.ok())
        self.top.bind("<Escape>", lambda event: self.cancel())

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
        self.master.geometry("720x960")  # main window size
        self.master.resizable(True, True)  # fixed main window size

        self.tab_rotator = TabRotator()
        self.thread = None

        self.url_listbox = tk.Listbox(master, width=90, height=30)
        self.url_listbox.pack(pady=10)
        
        start_btn_style = {
            "font": ("Arial", 10, "bold"),
            "width": 20,
            "height": 2,
            "bg": "#A1FFA4",
            "fg": "black",
            "activebackground": "#4dff00",
            "activeforeground": "black",
        }
        stop_btn_style = {
            "font": ("Arial", 10, "bold"),
            "width": 20,
            "height": 2,
            "bg": "#FFA1A1",
            "fg": "black",
            "activebackground": "#ff0000",
            "activeforeground": "black",
        }
        add_btn_style = {
            "font": ("Arial", 10, "bold"),
            "width": 20,
            "height": 2,
            "bg": "#A1E0FF",
            "fg": "black",
            "activebackground": "#0073ff",
            "activeforeground": "black",
        }
        remove_btn_style ={
            "font": ("Arial", 10, "bold"),
            "width": 20,
            "height": 2,
            "bg": "#E7A1FF",
            "fg": "black",
            "activebackground": "#ee00ff",
            "activeforeground": "black",
        }
        self.start_button = tk.Button(master, text="Start Rotating Tabs", command=self.start_rotation, **start_btn_style)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_rotation, **stop_btn_style)
        self.stop_button.pack(pady=10)

        self.add_button = tk.Button(master, text="Add URL", command=self.add_url, **add_btn_style)
        self.add_button.pack(pady=10)

        self.remove_button = tk.Button(master, text="Remove URL", command=self.remove_url, **remove_btn_style)
        self.remove_button.pack(pady=10)

        self.load_urls()

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_rotation(self):
        self.tab_rotator.urls = self.url_listbox.get(0, tk.END)
        if not self.tab_rotator.urls:
            messagebox.showwarning("No URLs", "Please add at least one URL.")
            return
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.tab_rotator.run, daemon=True)
            self.thread.start()

    def stop_rotation(self):
        self.tab_rotator.stop()
        if self.thread:
            self.thread.join()

    def add_url(self):
        dialog = UrlInputDialog(self.master, "Add URL")
        url = dialog.result
        if url:
            self.url_listbox.insert(tk.END, url)

    def remove_url(self):
        selected = self.url_listbox.curselection()
        if selected:
            self.url_listbox.delete(selected)

    def on_close(self):
        self.save_urls()
        self.stop_rotation()
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.master.destroy()

    def save_urls(self):
        with open("urls.txt", "w") as f:
            for url in self.url_listbox.get(0, tk.END):
                f.write(url + "\n")

    def load_urls(self):
        if os.path.exists("urls.txt"):
            with open("urls.txt", "r") as f:
                for line in f:
                    self.url_listbox.insert(tk.END, line.strip())


root = tk.Tk()
app = App(root)
root.mainloop()