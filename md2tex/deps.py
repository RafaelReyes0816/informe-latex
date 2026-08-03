"""Detección y reporte de dependencias del entorno LaTeX.

Centraliza las comprobaciones que necesita md2tex para compilar PDFs
(la cadena completa es: `latexmk` -> `perl` -> `pdflatex`/`xelatex`).

Se usa tanto desde la CLI (`cli.py`) como desde la GUI (`gui.py`) y sirve
para reemplazar al error interno de MiKTeX (`could not find the script
engine 'perl'`) por un mensaje claro al usuario.
"""

from __future__ import annotations

import shutil
import sys

# Herramientas que la cadena de compilación necesita tener en PATH.
_TOOLS = ("latexmk", "perl", "pdflatex")


def which(name: str) -> bool:
    """True si `name` está disponible en el PATH del sistema."""
    return shutil.which(name) is not None


def latex_dependencies() -> dict:
    """Estado de cada herramienta requerida."""
    return {tool: which(tool) for tool in _TOOLS}


def _platform_key() -> str:
    return "win32" if sys.platform == "win32" else (
        "darwin" if sys.platform == "darwin" else "linux"
    )


_HINTS = {
    "latexmk": {
        "linux": "Linux: sudo apt install texlive-latex-extra latexmk",
        "darwin": "macOS: instale MacTeX (https://www.tug.org/mactex/), luego `brew install latexmk`",
        "win32": "Windows: con MiKTeX instalado abra MiKTeX Console y añada el paquete 'latexmk', o ejecute `mpm --install=latexmk`",
    },
    "perl": {
        "linux": "Linux: `sudo apt install perl`",
        "darwin": "macOS: Perl está incluido con macOS",
        "win32": "Windows: instale Strawberry Perl (https://strawberryperl.com) — latexmk lo necesita",
    },
    "pdflatex": {
        "linux": "Linux: sudo apt install texlive-latex-base",
        "darwin": "macOS: MacTeX incluye pdflatex",
        "win32": "Windows: MiKTeX incluye pdflatex",
    },
}


def status_report() -> str:
    """Resumen legible estado/herramienta, para registrar en el log."""
    deps = latex_dependencies()
    lines = []
    for tool in _TOOLS:
        ok = deps[tool]
        mark = "✓" if ok else "✗"
        lines.append(f"{mark} {tool}: {'encontrado' if ok else 'no encontrado'}")
    return "\n".join(lines)


def missing_dependencies() -> list:
    deps = latex_dependencies()
    return [tool for tool in _TOOLS if not deps[tool]]


def ensure_latex_dependencies() -> str:
    """Valida las dependencias antes de compilar.

    - Si todo OK devuelve "" (cadena vacía).
    - Si falta algo, devuelve un mensaje amigable con qué falta, cómo
      instalarlo y el estado del entorno.
    """
    missing = missing_dependencies()
    if not missing:
        return ""

    plat = _platform_key()
    parts = ["No se puede compilar el PDF: faltan dependencias:"]
    parts.append("  " + ", ".join(missing))
    parts.append("")
    parts.append("Cómo instalar lo que falta:")
    for tool in missing:
        parts.append("  · " + _HINTS.get(tool, {}).get(plat, f"Instale {tool}."))
    parts.append("")
    parts.append("Estado del entorno:")
    parts.append(status_report())
    return "\n".join(parts)
