import ctypes
import os
import socket
import sys
import threading
import time
import traceback
import urllib.request
import webbrowser
from pathlib import Path


APP_NAME = "HPLC Data Visualizer"
MB_OK = 0x00000000
MB_ICONERROR = 0x00000010
MB_ICONINFORMATION = 0x00000040


def bundle_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def log_path() -> Path:
    base_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / APP_NAME / "logs"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "latest.log"


def show_message(message: str, flags: int) -> None:
    ctypes.windll.user32.MessageBoxW(None, message, APP_NAME, flags | MB_OK)


def find_available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def run_streamlit_worker(port: int) -> None:
    import streamlit.web.cli as streamlit_cli

    app_path = bundle_dir() / "web_app.py"
    os.chdir(bundle_dir())
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--server.headless=true",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
        "--global.developmentMode=false",
    ]
    raise SystemExit(streamlit_cli.main())


def wait_until_ready(url: str) -> bool:
    health_url = f"{url}/_stcore/health"
    for _ in range(120):
        try:
            with urllib.request.urlopen(health_url, timeout=1) as response:
                if response.status == 200:
                    return True
        except OSError:
            time.sleep(0.25)
    return False


def write_error_log() -> None:
    log_path().write_text(traceback.format_exc(), encoding="utf-8")


def browser_controller(url: str) -> None:
    if not wait_until_ready(url):
        show_message(
            f"The app could not start.\n\nDiagnostic log:\n{log_path()}",
            MB_ICONERROR,
        )
        os._exit(1)

    webbrowser.open(url, new=2)
    show_message(
        "The app is running locally in your browser.\n\n"
        "Keep this message open while using the app.\n"
        "Click OK when you are finished to stop it.",
        MB_ICONINFORMATION,
    )
    os._exit(0)


def run_launcher() -> None:
    port = find_available_port()
    url = f"http://127.0.0.1:{port}"
    threading.Thread(target=browser_controller, args=(url,), daemon=True).start()
    try:
        run_streamlit_worker(port)
    except BaseException:
        write_error_log()
        show_message(
            f"The app could not start.\n\nDiagnostic log:\n{log_path()}",
            MB_ICONERROR,
        )
        os._exit(1)


def run_smoke_test() -> None:
    port = find_available_port()
    url = f"http://127.0.0.1:{port}"

    def smoke_controller() -> None:
        os._exit(0 if wait_until_ready(url) else 1)

    threading.Thread(target=smoke_controller, daemon=True).start()
    run_streamlit_worker(port)


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--streamlit-worker":
        run_streamlit_worker(int(sys.argv[2]))
        return
    if len(sys.argv) == 2 and sys.argv[1] == "--smoke-test":
        run_smoke_test()
        return
    run_launcher()


if __name__ == "__main__":
    main()
