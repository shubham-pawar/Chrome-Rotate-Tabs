import time
import chromedriver_autoinstaller
from selenium import webdriver
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

class TabRotator:
    def __init__(self):
        self.urls = []
        self.interval = 10  # seconds
        self.driver = None
        self.running = False

    def start_browser(self):
        chromedriver_autoinstaller.install()
        self.driver = webdriver.Chrome()

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
                time.sleep(self.interval)

    def run(self):
        self.running = True
        self.start_browser()
        self.rotate_tabs()

    def stop(self):
        self.running = False
        if self.driver:
            self.driver.quit()
            self.driver = None  # Clear driver reference

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Tab Rotator")

        self.tab_rotator = TabRotator()
        self.thread = None

        self.start_button = tk.Button(master, text="Start Rotating Tabs", command=self.start_rotation)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_rotation)
        self.stop_button.pack(pady=10)

        self.add_button = tk.Button(master, text="Add URL", command=self.add_url)
        self.add_button.pack(pady=10)

        self.remove_button = tk.Button(master, text="Remove URL", command=self.remove_url)
        self.remove_button.pack(pady=10)

        self.url_listbox = tk.Listbox(master, width=50)
        self.url_listbox.pack(pady=10)

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
            self.thread.join()  # Wait for the thread to finish

    def add_url(self):
        url = simpledialog.askstring("Add URL", "Enter URL:")
        if url:
            self.url_listbox.insert(tk.END, url)

    def remove_url(self):
        selected = self.url_listbox.curselection()
        if selected:
            self.url_listbox.delete(selected)

    def on_close(self):
        self.stop_rotation()  # Stop rotation before closing
        if messagebox.askokcancel("Quit", "Do you really want to quit?"):
            self.master.destroy()

# Create the main window
root = tk.Tk()
app = App(root)

# Run the application
root.mainloop()