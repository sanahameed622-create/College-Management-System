"""
AcademiaPro Desktop App Launcher
Launches the Flask backend server in background and opens a clean,
native desktop application window (via Microsoft Edge / Google Chrome App Mode).
"""
import os
import sys
import time
import socket
import threading
import subprocess
import webbrowser

APP_PORT = 5000
APP_URL = f"http://127.0.0.1:{APP_PORT}"

def is_server_running(host="127.0.0.1", port=APP_PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def start_flask_server():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(base_dir, "app")
    sys.path.insert(0, app_dir)
    from app import app
    print(f"[*] Starting AcademiaPro Engine on {APP_URL}...")
    app.run(host="127.0.0.1", port=APP_PORT, debug=False, use_reloader=False)

def launch_native_window():
    # Wait for Flask to come online
    for _ in range(30):
        if is_server_running():
            break
        time.sleep(0.3)

    print("[*] Launching AcademiaPro Native Desktop Window...")

    # 1. Try Microsoft Edge in App Mode (Pre-installed on every Windows 10/11 system)
    edge_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ]
    for p in edge_paths:
        if os.path.exists(p):
            try:
                subprocess.Popen([p, f"--app={APP_URL}", "--window-size=1280,820"])
                return
            except Exception:
                pass

    # 2. Try Google Chrome in App Mode
    chrome_paths = [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
    ]
    for p in chrome_paths:
        if os.path.exists(p):
            try:
                subprocess.Popen([p, f"--app={APP_URL}", "--window-size=1280,820"])
                return
            except Exception:
                pass

    # 3. Fallback to standard default browser
    webbrowser.open(APP_URL)

if __name__ == "__main__":
    if not is_server_running():
        # Start server in daemon thread
        t = threading.Thread(target=start_flask_server, daemon=True)
        t.start()

    # Open app window
    launch_native_window()

    # Keep main process alive while server is up
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Exiting AcademiaPro ERP.")
        sys.exit(0)
