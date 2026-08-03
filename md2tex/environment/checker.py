from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_PLATFORM_KEY = "win32" if sys.platform == "win32" else (
    "darwin" if sys.platform == "darwin" else "linux"
)

_TOOLS = ("latexmk", "perl", "pdflatex", "xelatex", "lualatex", "kpsewhich")

_PACKAGES = [
    "amsmath", "amssymb", "graphicx", "hyperref", "booktabs",
    "array", "xcolor", "listings", "geometry", "setspace", "babel",
]

_HUMAN_TOOL_NAMES = {
    "latexmk": "latexmk",
    "perl": "Perl",
    "pdflatex": "pdfLaTeX",
    "xelatex": "XeLaTeX",
    "lualatex": "LuaLaTeX",
    "kpsewhich": "kpsewhich",
}

_HINTS = {
    "latexmk": {
        "linux": "Linux: sudo apt install texlive-latex-extra latexmk",
        "darwin": "macOS: MacTeX (https://www.tug.org/mactex/) incluye latexmk",
        "win32": "Windows: MiKTeX Console → paquetes → instale 'latexmk', o `mpm --install=latexmk`",
    },
    "perl": {
        "linux": "Linux: sudo apt install perl",
        "darwin": "macOS: Perl está incluido con macOS",
        "win32": "Windows: instale Strawberry Perl (https://strawberryperl.com); o el instalador de md2tex lo instala automáticamente",
    },
    "pdflatex": {
        "linux": "Linux: sudo apt install texlive-latex-base",
        "darwin": "macOS: MacTeX incluye pdflatex",
        "win32": "Windows: MiKTeX incluye pdflatex",
    },
    "xelatex": {
        "linux": "Linux: sudo apt install texlive-latex-base texlive-xetex",
        "darwin": "macOS: MacTeX incluye xelatex",
        "win32": "Windows: MiKTeX incluye xelatex",
    },
    "lualatex": {
        "linux": "Linux: sudo apt install texlive-luatex",
        "darwin": "macOS: MacTeX incluye lualatex",
        "win32": "Windows: MiKTeX incluye lualatex",
    },
    "kpsewhich": {
        "linux": "Linux: instale una distribución TeX completa (texlive-full)",
        "darwin": "macOS: MacTeX incluye kpsewhich",
        "win32": "Windows: MiKTeX incluye kpsewhich",
    },
}


def _detect_platform_key() -> str:
    return _PLATFORM_KEY


def _which(name: str) -> bool:
    return shutil.which(name) is not None


class EnvironmentChecker:
    TOOLS = _TOOLS

    @staticmethod
    def platform_key() -> str:
        return _detect_platform_key()

    @staticmethod
    def which(name: str) -> bool:
        return _which(name)

    @staticmethod
    def find_executable(name: str) -> str | None:
        return shutil.which(name)

    @classmethod
    def latex_dependencies(cls) -> dict[str, bool]:
        return {tool: _which(tool) for tool in cls.TOOLS}

    @classmethod
    def preferred_backend(cls) -> tuple:
        deps = cls.latex_dependencies()
        if deps["latexmk"] and deps["perl"]:
            return ("latexmk", "latexmk + perl disponibles")
        if deps["pdflatex"]:
            return ("pdflatex", "usando pdflatex (perl no disponible)")
        return (None, "no se encontró latexmk ni pdflatex")

    @classmethod
    def available_compilers(cls) -> list[str]:
        order = ["latexmk", "xelatex", "lualatex", "pdflatex"]
        return [c for c in order if _which(c)]

    @classmethod
    def missing(cls) -> list[str]:
        deps = cls.latex_dependencies()
        return [t for t in cls.TOOLS if not deps[t]]

    @classmethod
    def status_report(cls) -> str:
        deps = cls.latex_dependencies()
        lines = []
        for tool in cls.TOOLS:
            ok = deps[tool]
            mark = "✓" if ok else "✗"
            name = _HUMAN_TOOL_NAMES.get(tool, tool)
            lines.append(f"{mark} {name}: {'encontrado' if ok else 'no encontrado'}")
        return "\n".join(lines)

    @classmethod
    def packages_available(cls) -> dict[str, bool]:
        found = {}
        kpsewhich = shutil.which("kpsewhich") or shutil.which("miktex-kpsewhich")
        for pkg in _PACKAGES:
            found[pkg] = False
            if not kpsewhich:
                continue
            probe = f"{pkg}.sty"
            if pkg == "babel":
                probe = "spanish.ldf"
            try:
                r = subprocess.run(
                    [kpsewhich, probe],
                    capture_output=True, text=True, timeout=15,
                )
                found[pkg] = (r.returncode == 0 and bool(r.stdout.strip()))
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        return found

    @classmethod
    def packages_report(cls) -> str:
        pkgs = cls.packages_available()
        lines = []
        for pkg in _PACKAGES:
            ok = pkgs.get(pkg, False)
            mark = "✓" if ok else "✗"
            lines.append(f"  {mark} {pkg}")
        return "\n".join(lines)

    @classmethod
    def missing_packages(cls) -> list[str]:
        pkgs = cls.packages_available()
        if not pkgs:
            return []
        return [pkg for pkg in _PACKAGES if not pkgs.get(pkg)]

    @classmethod
    def ensure_compile_available(cls) -> str:
        backend, _ = cls.preferred_backend()
        if backend is not None:
            return ""
        parts = [
            "No se puede compilar el PDF: no hay un motor de compilación disponible.",
            "  Necesita latexmk+perl, o como mínimo pdflatex.",
            "",
            "Cómo instalar lo que falta:",
        ]
        for tool in ("latexmk", "pdflatex"):
            if not _which(tool):
                parts.append("  · " + _HINTS.get(tool, {}).get(_PLATFORM_KEY, f"Instale {tool}."))
        parts += ["", "Estado del entorno:", cls.status_report()]
        return "\n".join(parts)

    @classmethod
    def diagnose(cls) -> str:
        lines = [f"✓ md2tex {__version__}" if '__version__' in dir() else "✓ md2tex", ""]
        lines.append("Estado del entorno:")
        lines.append(cls.status_report())
        lines += ["", "Paquetes LaTeX (clave):"]
        pkgs = cls.packages_available()
        if pkgs:
            lines.append(cls.packages_report())
        else:
            lines.append("  (kpsewhich no disponible — se instalarán al vuelo)")
        lines.append("")
        from .compiler import LatexCompiler
        ok, msg = LatexCompiler.diagnose_compile()
        mark = "✓" if ok else "✗"
        lines.append(f"{mark} Compilación de prueba: {msg}")
        return "\n".join(lines)

    @classmethod
    def path_ok(cls) -> dict[str, bool]:
        return {tool: _which(tool) for tool in cls.TOOLS}

    @classmethod
    def check_path(cls) -> dict[str, bool]:
        return cls.path_ok()

    @classmethod
    def check_disk_space(cls) -> tuple[bool, str]:
        try:
            usage = shutil.disk_usage(".")
            free_gb = usage.free / (1024 ** 3)
            if free_gb < 0.5:
                return False, f"Espacio insuficiente: {free_gb:.2f} GB libre (mínimo 0.5 GB)"
            return True, f"{free_gb:.2f} GB libre"
        except Exception as e:
            return False, f"No se pudo comprobar espacio: {e}"

    @classmethod
    def check_permissions(cls) -> dict[str, bool]:
        permissions = {}
        permissions["write_temp"] = os.access(".", os.W_OK)
        permissions["write_home"] = os.access(os.path.expanduser("~"), os.W_OK)
        return permissions

    @staticmethod
    def detect_os() -> dict[str, str]:
        return {
            "platform": sys.platform,
            "platform_release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
        }


try:
    from md2tex import __version__
except ImportError:
    __version__ = "1.0.0"
