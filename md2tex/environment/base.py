from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class EnvironmentInfo:
    platform: str = ""
    platform_release: str = ""
    arch: str = ""
    path: list = field(default_factory=list)
    env_vars: dict = field(default_factory=dict)
    python_version: str = ""
    permissions: dict = field(default_factory=dict)


class EnvironmentBase(ABC):
    PLATFORM_KEY: str = ""
    TOOLS: tuple = ()
    PACKAGES: list = []
    PACKAGES_LATEX: list = []

    def __init__(self):
        self._info: EnvironmentInfo | None = None

    @property
    def platform_key(self) -> str:
        if not self.PLATFORM_KEY:
            if sys.platform == "win32":
                return "windows"
            elif sys.platform == "darwin":
                return "macos"
            return "linux"
        return self.PLATFORM_KEY

    @property
    def info(self) -> EnvironmentInfo:
        if self._info is None:
            self._info = self.detect_system()
        return self._info

    def detect_system(self) -> EnvironmentInfo:
        info = EnvironmentInfo()
        info.platform = sys.platform
        info.platform_release = platform.release()
        info.arch = platform.machine()
        info.path = os.environ.get("PATH", "").split(os.pathsep)
        info.python_version = sys.version
        info.env_vars = {
            "HOME": os.environ.get("HOME", ""),
            "USER": os.environ.get("USER", os.environ.get("USERNAME", "")),
        }
        return info

    def which(self, name: str) -> bool:
        return shutil.which(name) is not None

    def find_executable(self, name: str) -> str | None:
        return shutil.which(name)

    def get_version(self, name: str) -> str | None:
        try:
            result = subprocess.run(
                [name, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                lines = (result.stdout or result.stderr).strip().split("\n")
                return lines[0] if lines else None
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
        return None

    @abstractmethod
    def check_tools(self) -> dict[str, bool]:
        pass

    @abstractmethod
    def check_packages(self) -> dict[str, bool]:
        pass

    @abstractmethod
    def get_install_commands(self, missing_deps: list[str]) -> list[list[str]]:
        pass

    @abstractmethod
    def install_dependencies(self, deps: list[str]) -> bool:
        pass

    def get_available_compilers(self) -> list[str]:
        from .compiler import COMPILER_ORDER
        available = []
        for compiler in COMPILER_ORDER:
            if self.which(compiler):
                available.append(compiler)
        return available

    def check_disk_space(self) -> tuple[bool, str]:
        try:
            usage = shutil.disk_usage(".")
            free_gb = usage.free / (1024 ** 3)
            if free_gb < 0.5:
                return False, f"Espacio insuficiente: {free_gb:.2f} GB libre (mínimo 0.5 GB)"
            return True, f"{free_gb:.2f} GB libre"
        except Exception as e:
            return False, f"No se pudo comprobar espacio: {e}"

    def check_permissions(self) -> dict[str, bool]:
        permissions = {}
        permissions["write_temp"] = os.access(".", os.W_OK)
        permissions["write_home"] = os.access(os.path.expanduser("~"), os.W_OK)
        return permissions
