#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path
import os


def main_cli():
    root = Path(__file__).resolve().parent
    if os.name == "nt":
        venv_python = root / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = root / "venv" / "bin" / "python"

    if not venv_python.exists():
        print("venv not found, please create it first")
        sys.exit(1)

    main_script = root / "src" / "main.py"
    subprocess.run([str(venv_python), str(main_script)] + sys.argv[1:], check=True)


if __name__ == "__main__":
    main_cli()
