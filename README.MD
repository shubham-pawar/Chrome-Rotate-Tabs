# Tab Rotator Application

**Chrome Tab Rotator** is a Python GUI app that automatically rotates and refreshes Chrome tabs at set intervals. Built with tkinter for the interface and Selenium for browser automation. Ideal for showing dashboards on a TV or monitor.

![App UI](https://github.com/shubham-pawar/Chrome-Rotate-Tabs/blob/main/AppUI.png?raw=true)

## Key Features
- Open multiple URLs in separate Chrome tabs
- Auto-rotate tabs at a set interval
- Auto-refresh each tab when it is shown
- Easy URL management (add/remove), saved automatically to `urls.txt`
- Simple start/stop controls
- Works on TVs and high-DPI screens (buttons always visible)
- Works behind company proxies/firewalls (uses the Windows certificate store)

## 🛠 Prerequisites
- Windows
- Python 3.10+
- Google Chrome
- tkinter (included with Python on Windows)
- selenium 4.6+
- truststore

## Installation

1. **Clone the repository:**
```bash
   git clone https://github.com/shubham-pawar/Chrome-Rotate-Tabs.git
   cd Chrome-Rotate-Tabs
```

2. **Install dependencies:**
```bash
   pip install -r requirements.txt
```
   If several Python versions are installed, use the same one that runs the app, for example:
```bash
   py -3.13 -m pip install -r requirements.txt
```

## Usage
1. Run: `python app.py` (or `py -3.13 app.py`)
2. Click **Add URL** to add the pages you want to rotate
3. Click **Start Rotating Tabs**. Chrome opens with all URLs and starts rotating
4. Click **Stop** to stop rotating and close Chrome

URLs are saved to `urls.txt` (next to `app.py`) when you close the app and loaded the next time it starts.

To change how long each tab is shown (default 10 seconds), edit `self.interval` in the `TabRotator` class in `app.py`.

## Offline / Locked-down Machines
Selenium downloads the matching ChromeDriver automatically. If the machine has no internet access:
1. Check your Chrome version: Chrome → Settings → About Chrome
2. Download the matching **win64** `chromedriver.exe` from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)
3. Put `chromedriver.exe` in the same folder as `app.py`. The app uses it automatically

## Troubleshooting
| Error | Fix |
|---|---|
| `SSL: CERTIFICATE_VERIFY_FAILED` | Run `pip install truststore` |
| `This version of ChromeDriver only supports Chrome version X` | Replace or delete the local `chromedriver.exe` |
| `ModuleNotFoundError` | Install dependencies with the same Python that runs the app |

## License
This project is licensed under the **Apache License 2.0**.
See the [LICENSE](https://github.com/shubham-pawar/Chrome-Rotate-Tabs/blob/main/LICENSE) file for details.

## Author
[Shubham Pawar](https://github.com/shubham-pawar)

## Support
If you like this project, please leave a star ⭐