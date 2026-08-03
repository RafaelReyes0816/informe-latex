from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .base import EnvironmentBase, EnvironmentInfo
from .checker import EnvironmentChecker


class MacOSEnvironment(EnvironmentBase):
    PLATFORM_KEY = "macos"
    TOOLS = ("latexmk", "perl", "pdflatex", "xelatex", "lualatex", "kpsewhich")
    PACKAGES = [
        "amsmath", "amssymb", "graphicx", "hyperref", "booktabs",
        "array", "xcolor", "listings", "geometry", "setspace", "babel",
        "fontawesome5", "fancyhdr", "tcolorbox",
    ]

    def detect_system(self) -> EnvironmentInfo:
        import platform as plat
        info = super().detect_system()
        info.platform = plat.system()
        info.platform_release = plat.release()
        info.arch = plat.machine()
        return info

    def check_tools(self) -> dict[str, bool]:
        return EnvironmentChecker.latex_dependencies()

    def check_packages(self) -> dict[str, bool]:
        return EnvironmentChecker.packages_available()

    def brew_available(self) -> bool:
        return shutil.which("brew") is not None

    def mactex_available(self) -> bool:
        return shutil.which("pdflatex") is not None

    def get_install_commands(self, missing_deps: list[str]) -> list[list[str]]:
        from .installer import DependencyInstaller
        installer = DependencyInstaller()
        return installer._macos_install_commands(missing_deps)

    def install_dependencies(self, deps: list[str]) -> bool:
        from .installer import DependencyInstaller
        installer = DependencyInstaller()
        return installer.install_dependencies(deps)

    def install_brew(self) -> bool:
        try:
            script = (
                '/bin/bash -c "$(curl -fsSL '
                'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            )
            result = subprocess.run(
                script, shell=True, capture_output=True, text=True, timeout=600,
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_mactex(self) -> bool:
        if not self.brew_available():
            return False
        try:
            result = subprocess.run(
                ["brew", "install", "--cask", "mactex"],
                capture_output=True, text=True, timeout=1800,
            )
            return result.returncode == 0
        except Exception:
            return False

    def repair(self) -> tuple[bool, str, list[str]]:
        actions = []
        if not self.brew_available():
            actions.append("Instale Homebrew desde: https://brew.sh")
            if self.install_brew():
                actions.append("Homebrew instalado")
                return True, "macOS: Homebrew instalado", actions
            return False, "macOS: requiere Homebrew", actions

        if not self.mactex_available():
            actions.append("Instalando MacTeX (descarga grande)...")
            if self.install_mactex():
                actions.append("MacTeX instalado")
                return True, "macOS: MacTeX instalado", actions
            return False, "macOS: requiere MacTeX", actions

        actions.append("Entorno macOS verificado")
        return True, "macOS: entorno listo", actions
