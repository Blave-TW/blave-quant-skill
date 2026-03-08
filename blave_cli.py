import sys
import subprocess
from pathlib import Path
import os


def main_cli():
    if len(sys.argv) < 2:
        print("usage: blave <command> [args]")
        return

    root = Path(__file__).resolve().parent
    # venv Python 路徑
    if os.name == "nt":
        venv_python = root / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = root / "venv" / "bin" / "python"

    if not venv_python.exists():
        print("venv not found, please create it first")
        sys.exit(1)

    # 執行 main.py 並傳入所有 CLI 參數
    main_script = root / "src" / "main.py"
    subprocess.run(
        [str(venv_python), str(main_script)] + sys.argv[1:],
        check=True,
    )
