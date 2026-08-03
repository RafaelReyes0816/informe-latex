#!/usr/bin/env python3
"""Build script for md2tex — executables and platform installers.

Usage:
    python build.py               # clean + build all + installer
    python build.py gui           # only GUI binary
    python build.py cli           # only CLI binary
    python build.py binaries      # GUI + CLI binaries
    python build.py installer     # platform installer from existing binaries
    python build.py clean         # remove build artifacts
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIST = HERE / "dist"
BUILD_DIR = HERE / "build"

os.chdir(HERE)
sys.path.insert(0, str(HERE))
from md2tex import __version__ as VERSION


def get_os_name() -> str:
    s = platform.system()
    return {"Linux": "linux", "Windows": "windows", "Darwin": "macos"}.get(s, s.lower())


def get_sep() -> str:
    return ";" if get_os_name() == "windows" else ":"


def clean():
    for d in [DIST, BUILD_DIR]:
        if d.is_dir():
            shutil.rmtree(d)
    for f in HERE.glob("*.spec"):
        f.unlink(missing_ok=True)
    print("Cleaned build/ dist/ *.spec")


def build_binary(gui: bool = True):
    if not shutil.which("pyinstaller"):
        print("Installing pyinstaller...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            check=True,
        )

    os_name = get_os_name()
    suffix = "" if gui else "-cli"
    exe_ext = ".exe" if os_name == "windows" else ""
    name = f"md2tex-{os_name}{suffix}"

    cmd = [
        "pyinstaller",
        "--onefile",
        "--name", name,
        "--add-data", f"templates{get_sep()}templates",
        "--distpath", str(DIST),
        "--workpath", str(BUILD_DIR),
        "--specpath", str(HERE),
    ]
    if gui:
        cmd.append("--collect-data")
        cmd.append("customtkinter")
        if os_name == "windows":
            cmd.append("--noconsole")
        elif os_name == "macos":
            cmd.append("--windowed")
    cmd.append(str(HERE / "md2tex" / "__main__.py"))

    print(f"Building: {name}{exe_ext}")
    subprocess.run(cmd, check=True)
    binary = DIST / f"{name}{exe_ext}"
    if binary.is_file():
        print(f"OK: {binary} ({binary.stat().st_size / 1024:.0f} KB)")
    return binary


def build_installer():
    os_name = get_os_name()
    dist_dir = DIST.resolve()

    if os_name == "linux":
        deb_script = HERE / "installer" / "linux" / "create-deb.sh"
        subprocess.run(["bash", str(deb_script), VERSION, str(dist_dir / f"md2tex-{os_name}")], check=True)

    elif os_name == "macos":
        # Build .app bundle (PyInstaller --onedir --windowed for macOS)
        name = f"md2tex-macos"
        app = dist_dir / f"{name}.app"
        if not app.is_dir():
            print("Building .app bundle...")
            subprocess.run([
                "pyinstaller", "--onedir", "--windowed",
                "--name", name,
                "--add-data", f"templates:templates",
                "--collect-data", "customtkinter",
                "--distpath", str(dist_dir),
                "--workpath", str(BUILD_DIR),
                "--specpath", str(HERE),
                str(HERE / "md2tex" / "__main__.py"),
            ], check=True)
        dmg_script = HERE / "installer" / "macos" / "create-dmg.sh"
        subprocess.run(["bash", str(dmg_script), VERSION, str(app)], check=True)

    elif os_name == "windows":
        # Ensure we have the binaries
        for variant in ["", "-cli"]:
            exe = dist_dir / f"md2tex-windows{variant}.exe"
            if not exe.is_file():
                print(f"Missing: {exe}. Run 'python build.py binaries' first.")
                sys.exit(1)

        # Find iscc
        iscc = shutil.which("iscc")
        if not iscc:
            iscc_paths = [
                "C:/Program Files (x86)/Inno Setup 6/iscc.exe",
                "C:/Program Files/Inno Setup 6/iscc.exe",
            ]
            for p in iscc_paths:
                if Path(p).is_file():
                    iscc = p
                    break
        if not iscc:
            print("Inno Setup (iscc) not found. Install from https://jrsoftware.org/isdl.php")
            print("Or via Chocolatey: choco install innosetup")
            sys.exit(1)

        env = {**os.environ, "MD2TEX_VERSION": VERSION}
        iss = HERE / "installer" / "windows" / "setup.iss"
        subprocess.run([iscc, str(iss)], check=True, env=env)

    print(f"\nInstallers in {dist_dir}/")
    for f in sorted(dist_dir.iterdir()):
        if f.suffix in (".deb", ".dmg", ".exe", ".AppImage") or ".deb" in f.name:
            print(f"  {f.name}")


def main():
    cmds = {
        "clean": clean,
        "gui": lambda: build_binary(gui=True),
        "cli": lambda: build_binary(gui=False),
        "binaries": lambda: [build_binary(True), build_binary(False)],
        "installer": build_installer,
    }

    args = [a for a in sys.argv[1:] if not a.startswith("-")] or ["all"]

    if "all" in args:
        clean()
        build_binary(True)
        build_binary(False)
        build_installer()
        print("\nAll builds complete.")
        return

    for a in args:
        fn = cmds.get(a)
        if fn:
            fn()
        else:
            print(f"Unknown: {a}. Options: {' | '.join(cmds)} | all")
            sys.exit(1)


if __name__ == "__main__":
    main()
