from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .base import EnvironmentBase
from .checker import EnvironmentChecker


class DependencyInstaller(EnvironmentBase):
    def __init__(self):
        super().__init__()
        self._platform_key = self.platform_key

    @property
    def platform_key(self) -> str:
        if sys.platform == "win32":
            return "windows"
        elif sys.platform == "darwin":
            return "macos"
        return "linux"

    def check_tools(self) -> dict[str, bool]:
        return EnvironmentChecker.latex_dependencies()

    def check_packages(self) -> dict[str, bool]:
        return EnvironmentChecker.packages_available()

    def get_install_commands(self, missing_deps: list[str]) -> list[list[str]]:
        commands = []
        if self._platform_key == "windows":
            commands.extend(self._windows_install_commands(missing_deps))
        elif self._platform_key == "macos":
            commands.extend(self._macos_install_commands(missing_deps))
        else:
            commands.extend(self._linux_install_commands(missing_deps))
        return commands

    def _linux_install_commands(self, missing_deps: list[str]) -> list[list[str]]:
        commands = []
        if not shutil.which("apt"):
            return commands

        install_deps = []
        if "pdflatex" in missing_deps or "latexmk" in missing_deps:
            install_deps.extend(["texlive-latex-base", "texlive-latex-extra",
                                 "texlive-fonts-recommended", "latexmk"])
        if "perl" in missing_deps:
            install_deps.append("perl")
        if "xelatex" in missing_deps:
            install_deps.extend(["texlive-xetex"])
        if "lualatex" in missing_deps:
            install_deps.extend(["texlive-luatex"])

        if install_deps:
            commands.append(["sudo", "apt", "update"])
            commands.append(["sudo", "apt", "install", "-y"] + install_deps)

        return commands

    def _macos_install_commands(self, missing_deps: list[str]) -> list[list[str]]:
        commands = []
        if not shutil.which("brew"):
            commands.append(["/bin/bash", "-c",
                             'echo "Instale Homebrew: https://brew.sh"'])
            return commands

        install_deps = []
        if "latexmk" in missing_deps:
            install_deps.append("latexmk")
        if "pdflatex" in missing_deps:
            commands.append(["brew", "install", "--cask", "mactex"])
        if "perl" in missing_deps:
            install_deps.append("perl")

        if install_deps:
            commands.append(["brew", "install"] + install_deps)

        return commands

    def _windows_install_commands(self, missing_deps: list[str]) -> list[list[str]]:
        commands = []
        if "pdflatex" in missing_deps or "latexmk" in missing_deps or "kpsewhich" in missing_deps:
            commands.append(self._download_miktex())
        if "perl" in missing_deps:
            commands.append(self._download_strawberry_perl())
        return commands

    def install_dependencies(self, deps: list[str]) -> bool:
        commands = self.get_install_commands(deps)
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=600,
                )
                if result.returncode != 0:
                    return False
            except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
                return False
        return True

    def install(self) -> bool:
        tools = EnvironmentChecker.latex_dependencies()
        missing = [t for t, found in tools.items() if not found]
        if not missing:
            return True
        return self.install_dependencies(missing)

    @staticmethod
    def _download_miktex() -> list[str]:
        url = "https://miktex.org/download/win/miktexsetup-x64.zip"
        return ["powershell", "-Command",
                f"Invoke-WebRequest -Uri '{url}' -OutFile 'miktexsetup.zip'; "
                "Expand-Archive -Path 'miktexsetup.zip' -DestinationPath 'miktex'; "
                "cd miktex; .\\miktexsetup.exe --local-package-repository=. "
                "--package-set=complete download; "
                ".\\miktexsetup.exe --local-package-repository=. install --service>"]

    @staticmethod
    def _download_strawberry_perl() -> list[str]:
        url = ("https://github.com/StrawberryPerl/Perl/releases/download/"
               "5.38.7.1/StrawberryPerl-5.38.7.1-64bit.msi")
        return ["powershell", "-Command",
                f"Invoke-WebRequest -Uri '{url}' -OutFile 'strawberry.msi'; "
                "msiexec /i strawberry.msi /quiet /norestart"]

    def get_install_hints(self) -> dict[str, str]:
        hints = {}
        for tool in EnvironmentChecker.TOOLS:
            if EnvironmentChecker.which(tool):
                continue
            hints[tool] = self._get_tool_hint(tool)
        return hints

    @staticmethod
    def _get_tool_hint(tool: str) -> str:
        hint_map = {
            "latexmk": {
                "linux": "sudo apt install texlive-latex-extra latexmk",
                "darwin": "brew install latexmk",
                "windows": "MiKTeX Console → paquetes → instale 'latexmk'",
            },
            "pdflatex": {
                "linux": "sudo apt install texlive-latex-base",
                "darwin": "brew install --cask mactex",
                "windows": "El instalador de md2tex instala MiKTeX automáticamente",
            },
            "perl": {
                "linux": "sudo apt install perl",
                "darwin": "Perl está incluido con macOS",
                "windows": "El instalador instala Strawberry Perl, o descargue desde https://strawberryperl.com",
            },
        }
        if sys.platform == "win32":
            key = "windows"
        elif sys.platform == "darwin":
            key = "darwin"
        else:
            key = "linux"
        return hint_map.get(tool, {}).get(key, f"Instale {tool}")

    def install_all_needed(self) -> tuple[bool, str, list[str]]:
        missing_tools = EnvironmentChecker.missing()
        if not missing_tools:
            return True, "Todas las dependencias están instaladas", []

        actions = []
        if self._platform_key == "windows":
            success = self._windows_auto_install(missing_tools, actions)
        elif self._platform_key == "linux":
            success = self._linux_auto_install(missing_tools, actions)
        elif self._platform_key == "macos":
            success = self._macos_auto_install(missing_tools, actions)
        else:
            return False, "Sistema operativo no soportado", []

        message = "Instalación completada" if success else "Instalación fallida"
        return success, message, actions

    def _windows_auto_install(self, missing_tools: list[str], actions: list[str]) -> bool:
        if "pdflatex" in missing_tools or "latexmk" in missing_tools or "kpsewhich" in missing_tools:
            actions.append("Descargando e instalando MiKTeX...")
            return self._install_miktex(actions)
        return False

    def _macos_auto_install(self, missing_tools: list[str], actions: list[str]) -> bool:
        if "pdflatex" in missing_tools or "latexmk" in missing_tools:
            actions.append("Instalando MacTeX (descarga grande)...")
            if shutil.which("brew"):
                try:
                    subprocess.run(
                        ["brew", "install", "--cask", "mactex"],
                        timeout=1800,
                    )
                    return True
                except Exception:
                    return False
            return False
        return False

    def _linux_auto_install(self, missing_tools: list[str], actions: list[str]) -> bool:
        commands = self._linux_install_commands(missing_tools)
        for cmd in commands:
            actions.append(f"Ejecutando: {' '.join(cmd)}")
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                if result.returncode != 0:
                    actions.append(f"Error: {result.stderr[:200] if result.stderr else 'desconocido'}")
                    return False
            except Exception as e:
                actions.append(f"Excepción: {e}")
                return False
        return True

    def _install_miktex(self, actions: list[str]) -> bool:
        try:
            script = (
                "$url = 'https://miktex.org/download/win/miktexsetup-x64.zip';"
                "$zipPath = '$env:TEMP\\miktexsetup.zip';"
                "Invoke-WebRequest -Uri $url -OutFile $zipPath;"
                "Expand-Archive -Path $zipPath -DestinationPath '$env:TEMP\\miktex';"
                "Set-Location '$env:TEMP\\miktex';"
                ".\\miktexsetup.exe --local-package-repository=. "
                "--package-set=complete download;"
                ".\\miktexsetup.exe --local-package-repository=. install;"
            )
            result = subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True, text=True, timeout=1800,
            )
            if result.returncode == 0:
                actions.append("MiKTeX instalado correctamente")
                return True
            actions.append(f"Error instalando MiKTeX: {result.stderr[:300]}")
            return False
        except Exception as e:
            actions.append(f"Error: {e}")
            return False
