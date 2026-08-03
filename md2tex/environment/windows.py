from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .base import EnvironmentBase, EnvironmentInfo
from .checker import EnvironmentChecker


class WindowsEnvironment(EnvironmentBase):
    PLATFORM_KEY = "windows"
    TOOLS = ("latexmk", "perl", "pdflatex", "xelatex", "lualatex", "kpsewhich")
    PACKAGES = [
        "amsmath", "amssymb", "graphicx", "hyperref", "booktabs",
        "array", "xcolor", "listings", "geometry", "setspace", "babel",
        "fontawesome5", "fancyhdr", "tcolorbox",
    ]

    def detect_system(self) -> EnvironmentInfo:
        info = super().detect_system()
        if sys.platform == "win32":
            import platform as plat
            info.platform = f"Windows {plat.version()}"
            info.arch = "x86_64" if plat.machine().endswith("64") else platform.machine()
        return info

    def check_tools(self) -> dict[str, bool]:
        return EnvironmentChecker.latex_dependencies()

    def check_packages(self) -> dict[str, bool]:
        return EnvironmentChecker.packages_available()

    def get_install_commands(self, missing_deps: list[str]) -> list[list[str]]:
        from .installer import DependencyInstaller
        installer = DependencyInstaller()
        return installer._windows_install_commands(missing_deps)

    def install_dependencies(self, deps: list[str]) -> bool:
        from .installer import DependencyInstaller
        installer = DependencyInstaller()
        return installer.install_dependencies(deps)

    def miktex_available(self) -> bool:
        return shutil.which("initexmf") is not None

    def update_fndb(self) -> None:
        _run_silent(["initexmf", "--update-fndb"])

    def enable_autoinstall(self) -> None:
        _run_silent(["initexmf", "--set-config-value=[MPM]AutoInstall=1"])

    def update_package_db(self) -> None:
        _run_silent(["mpm", "--update-db"])

    def prepare_miktex(self) -> None:
        self.update_fndb()
        self.enable_autoinstall()

    def repair(self) -> tuple[bool, str, list[str]]:
        actions = []
        self.prepare_miktex()
        actions.append("MiKTeX preparado (FDNB actualizada, autoinstalación habilitada)")
        self.update_package_db()
        actions.append("Base de datos de paquetes actualizada")
        return True, "Windows: entorno preparado", actions


def _run_silent(cmd: list) -> None:
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
