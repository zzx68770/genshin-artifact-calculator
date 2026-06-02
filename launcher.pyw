#!/usr/bin/env python3
"""
原神圣遗物计算器启动器
双击启动 → 打开独立应用窗口 → 关闭窗口 → 服务自动停止
无弹窗、无黑框、无闪烁
"""

import subprocess
import sys
import time
import os
import shutil
import tempfile

PORT = 8501


def kill_old_python():
    """Kill residual python processes (exclude self)."""
    my_pid = os.getpid()
    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "python.exe",
             "/fi", f"PID ne {my_pid}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(1)
    except Exception:
        pass


def start_streamlit():
    """Start Streamlit server hidden."""
    return subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py",
         "--server.headless", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def find_browser():
    """Find Chrome or Edge executable path."""
    candidates = [
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def open_app_window(browser_path, port, temp_dir):
    """Open URL as a standalone app window with isolated profile."""
    return subprocess.Popen(
        [browser_path,
         f"--app=http://localhost:{port}",
         "--window-size=1280,800",
         f"--user-data-dir={temp_dir}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # 1. Clean up old processes
    kill_old_python()

    # 2. Start Streamlit
    server_proc = start_streamlit()
    time.sleep(5)

    # 3. Create temp profile dir for isolated browser instance
    temp_dir = tempfile.mkdtemp(prefix="artifact_calc_")

    try:
        browser_path = find_browser()
        if browser_path:
            # Open standalone app window
            browser_proc = open_app_window(browser_path, PORT, temp_dir)
            # Block until user closes the window
            browser_proc.wait()
        else:
            # Fallback: open in default browser
            import webbrowser
            webbrowser.open(f"http://localhost:{PORT}")
            # Keep server running until manually killed
            server_proc.wait()
    finally:
        # 4. Cleanup: stop server + remove temp profile
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except Exception:
            server_proc.kill()
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
