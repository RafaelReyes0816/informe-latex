from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .base import EnvironmentBase, EnvironmentInfo
from .checker import EnvironmentChecker


class LinuxEnvironment(EnvironmentBase):
    PLATFORM_KEY = "linux"
    TOOLS = ("xelatex", "lualatex", "pdflatex", "kpsewhich", "latexmk", "perl")
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
        try:
            import distro
            info.distro = distro.name()
            info.distro_version = distro.version()
        except ImportError:
            info.distro = "desconocida"
            info.distro_version = "desconocida"
        return info

    def detect_distro(self) -> str:
        if sys.platform != "linux":
            return ""
        if Path("/etc/os-release").exists():
            for line in Path("/etc/os-release").read_text().splitlines():
                if line.startswith("ID="):
                    return line.split("=")[1].strip('"\'')
        if Path("/etc/redhat-release").exists():
            return "redhat"
        return "desconocida"

    def detect_package_manager(self) -> str:
        if shutil.which("apt"):
            return "apt"
        elif shutil.which("dnf"):
            return "dnf"
        elif shutil.which("pacman"):
            return "pacman"
        elif shutil.which("zypper"):
            return "zypper"
        elif shutil.which("emerge"):
            return "portage"
        return "desconocido"

    def check_tools(self) -> dict[str, bool]:
        return EnvironmentChecker.latex_dependencies()

    def check_packages(self) -> dict[str, bool]:
        return EnvironmentChecker.packages_available()

    def get_install_commands(self, missing_deps: list[str]) -> list[list[str]]:
        from .installer import DependencyInstaller
        installer = DependencyInstaller()
        return installer._linux_install_commands(missing_deps)

    def install_dependencies(self, deps: list[str]) -> bool:
        from .installer import DependencyInstaller
        installer = DependencyInstaller()
        return installer.install_dependencies(deps)

    def get_package_manager_hint(self, distro_id: str | None = None) -> str:
        pm = self.detect_package_manager()
        hints = {
            "apt": "sudo apt update && sudo apt install -y texlive-latex-base texlive-xetex python3-tk",
            "dnf": "sudo dnf install -y texlive-scheme-basic texlive-xetex python3-tk",
            "pacman": "sudo pacman -S --noconfirm texlive-most python tk",
            "zypper": "sudo zypper install -y texlive-scheme-basic texlive-xetex",
        }
        return hints.get(pm, "Instale LaTeX manualmente")

    def repair(self) -> tuple[bool, str, list[str]]:
        actions = []
        pm = self.detect_package_manager()
        if pm == "apt":
            actions.append("Use: sudo apt update && sudo apt install -y texlive-latex-base texlive-xetex")
        elif pm == "dnf":
            actions.append("Use: sudo dnf install -y texlive-scheme-basic texlive-xetex")
        elif pm == "pacman":
            actions.append("Use: sudo pacman -S --noconfirm texlive-core")
        else:
            actions.append("Use su gestor de paquetes para instalar: texlive-latex-base, texlive-xetex")
        return False, "Linux: requiere instalación manual", actions
