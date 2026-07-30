#!/usr/bin/env python3
"""Build script for creating md2tex executables with PyInstaller."""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIST = HERE / "dist"
BUILD = HERE / "build"
SPEC = HERE / "md2tex.spec"
NAME = "md2tex"


def get_os_name() -> str:
    s = platform.system()
    return {"Linux": "linux", "Windows": "windows", "Darwin": "macos"}.get(s, s.lower())


def clean():
    for d in [DIST, BUILD]:
        if d.is_dir():
            shutil.rmtree(d)
    for f in HERE.glob("*.spec"):
        f.unlink(missing_ok=True)
    print("Cleaned build/ dist/ *.spec")


def build(gui: bool = True):
    if not shutil.which("pyinstaller"):
        print("Installing pyinstaller...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            check=True, cwd=HERE,
        )

    os_name = get_os_name()
    suffix = "" if gui else "-cli"
    exe_ext = ".exe" if os_name == "windows" else ""
    out_name = f"{NAME}-{os_name}{suffix}{exe_ext}"

    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", out_name.replace(exe_ext, ""),
        "--add-data", f"templates{chr(59) if os_name == 'windows' else ':'}templates",
        "--distpath", str(DIST),
        "--workpath", str(BUILD),
        "--specpath", str(HERE),
    ]
    if gui:
        cmd.append("--noconsole")
    cmd.append(str(HERE / "md2tex" / "__main__.py"))

    print(f"Building: {out_name}")
    subprocess.run(cmd, check=True, cwd=HERE)
    print(f"Done: {DIST / out_name}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build md2tex executables")
    parser.add_argument("action", choices=["clean", "gui", "cli", "all"], default="all", nargs="?")
    args = parser.parse_args()

    if args.action == "clean":
        clean()
    elif args.action == "gui":
        build(gui=True)
    elif args.action == "cli":
        build(gui=False)
    else:
        clean()
        build(gui=True)
        build(gui=False)
        print("Build complete. Files in dist/")
