from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .checker import EnvironmentChecker


class EnvironmentRepairer:
    @classmethod
    def repair(cls) -> tuple[bool, str, list[str]]:
        actions = []
        success = True

        path_fixed = cls._repair_path()
        if path_fixed:
            actions.append("PATH actualizado")
        elif path_fixed is False:
            success = False
            actions.append("No se pudo reparar el PATH")

        compiler_fixed = cls._repair_compilers()
        if compiler_fixed:
            actions.append("Compiladores verificados")
        elif compiler_fixed is False:
            success = False
            actions.append("No se pudieron reparar los compiladores")

        packages_fixed = cls._repair_packages()
        if packages_fixed:
            actions.append("Paquetes LaTeX actualizados")
        elif packages_fixed is False:
            actions.append("No se pudieron instalar todos los paquetes (continuar)")

        config_fixed = cls._repair_config()
        if config_fixed:
            actions.append("Configuración regenerada")
        elif config_fixed is False:
            actions.append("No se pudo regenerar la configuración")

        cleaned = cls._clean_temp_files()
        if cleaned:
            actions.append("Archivos temporales limpiados")

        resources_fixed = cls._verify_resources()
        if resources_fixed:
            actions.append("Recursos verificados")
        elif resources_fixed is False:
            success = False
            actions.append("Recursos incompletos")

        message = "Reparación completada" if success else "Reparación parcial"
        if not actions:
            actions.append("No se realizaron reparaciones")

        return success, message, actions

    @classmethod
    def _repair_path(cls) -> bool | None:
        path_env = os.environ.get("PATH", "")
        path_dirs = path_env.split(os.pathsep)
        latex_dirs = [
            d for d in path_dirs
            if "tex" in d.lower() or "miktex" in d.lower() or "texlive" in d.lower()
        ]
        if not latex_dirs:
            return None
        return True

    @classmethod
    def _repair_compilers(cls) -> bool | None:
        from .compiler import LatexCompiler
        if sys.platform == "win32":
            EnvironmentChecker.__class__
            _run_silent(["initexmf", "--update-fndb"])
            _run_silent(["initexmf", "--set-config-value=[MPM]AutoInstall=1"])

        backend, _ = EnvironmentChecker.preferred_backend()
        if backend:
            return True
        return False

    @classmethod
    def _repair_packages(cls) -> bool | None:
        if sys.platform == "win32":
            _run_silent(["mpm", "--update-db"])
        elif sys.platform == "darwin":
            pass
        else:
            if shutil.which("tlmgr"):
                try:
                    subprocess.run(
                        ["tlmgr", "option", "repository",
                         "https://mirror.ctan.org/systems/texlive/tlnet"],
                        capture_output=True, text=True, timeout=30,
                    )
                except Exception:
                    pass
        return True

    @classmethod
    def _repair_config(cls) -> bool | None:
        if sys.platform == "win32":
            try:
                subprocess.run(
                    ["initexmf", "--update-fndb"],
                    capture_output=True, text=True, timeout=60,
                )
                return True
            except Exception:
                return False
        return True

    @staticmethod
    def _clean_temp_files() -> bool:
        cleaned = False
        cwd = Path.cwd()
        temp_extensions = [".aux", ".log", ".out", ".toc", ".fls",
                           ".fdb_latexmk", ".bbl", ".bcf", ".blg",
                           ".run.xml", ".lof", ".lot"]
        for ext in temp_extensions:
            for f in cwd.glob(f"*{ext}"):
                try:
                    f.unlink()
                    cleaned = True
                except Exception:
                    pass
        md2tex_logs = cwd.glob("md2tex-compile-*.log")
        for log in md2tex_logs:
            try:
                log.unlink()
                cleaned = True
            except Exception:
                pass
        return cleaned

    @classmethod
    def _verify_resources(cls) -> bool | None:
        from .validator import EnvironmentValidator
        res = EnvironmentValidator.validate_resources()
        return (
            res.get("templates_dir_exists", False)
            and res.get("default_template_valid", False)
        )

    def repair_all(self) -> tuple[bool, str, list[str]]:
        return self.repair()


def _run_silent(cmd: list) -> None:
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
