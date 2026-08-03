"""Detección y reporte de dependencias del entorno LaTeX.

Centraliza las comprobaciones que necesita md2tex para compilar PDFs
(la cadena completa es: `latexmk` -> `perl` -> `pdflatex`/`xelatex`).

Se usa tanto desde la CLI (`cli.py`) como desde la GUI (`gui.py`) y sirve
para reemplazar al error interno de MiKTeX (`could not find the script
engine 'perl'`) por un mensaje claro al usuario.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

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

    - Si hay un motor usable devuelve "" (cadena vacía).
    - Si no, devuelve un mensaje amigable con qué falta, cómo instalarlo
      y el estado del entorno.

    Un motor es usable cuando (latexmk AND perl) OR (pdflatex). El backend
    `pdflatex` (sin perl) se usa cuando falta perl, por lo que no es
    estrictamente obligatorio.
    """
    backend, _ = preferred_backend()
    if backend is not None:
        return ""

    plat = _platform_key()
    parts = [
        "No se puede compilar el PDF: no hay un motor de compilación disponible.",
        "  Necesita latexmk+perl, o como mínimo pdflatex.",
        "",
        "Cómo instalar lo que falta:",
    ]
    for tool in ("latexmk", "pdflatex"):
        if not which(tool):
            parts.append("  · " + _HINTS.get(tool, {}).get(plat, f"Instale {tool}."))
    parts.append("")
    parts.append("Estado del entorno:")
    parts.append(status_report())
    return "\n".join(parts)


def preferred_backend() -> tuple:
    """Devuelve (backend, detalle) según lo disponible en el PATH.

    Prioridad 1: ``latexmk`` + ``perl`` (máxima fidelidad, resuelve TOC/bib).
    Prioridad 2: ``pdflatex`` (fallback, sin perl; 2 pasadas para TOC).
    Si ninguno: (None, motivo).
    """
    deps = latex_dependencies()
    if deps["latexmk"] and deps["perl"]:
        return ("latexmk", "latexmk + perl disponibles")
    if deps["pdflatex"]:
        return ("pdflatex", "usando pdflatex (perl no disponible)")
    return (None, "no se encontró latexmk ni pdflatex")


def ensure_compile_available() -> str:
    """Mensake amigable cuando no hay ningún motor de compilación usable."""
    return ensure_latex_dependencies()


def compile_pdf(tex_path, cwd=None) -> tuple:
    """Compila ``tex_path`` a PDF dentro de ``cwd``.

    Selecciona el backend disponible (latexmk preferido; pdflatex como
    *fallback* cuando falta perl). Devuelve ``(ok, mensaje)``. El ``cwd``
    debe ser el directorio donde vive el ``.tex`` (ahí resuelve
    ``\\graphicspath{{figures/}}``).
    """
    tex_name = Path(tex_path).name
    cwd = str(Path(cwd) if cwd else Path(tex_path).parent)

    backend, detail = preferred_backend()
    if backend is None:
        return False, ensure_compile_available()

    if backend == "latexmk":
        cmd = ["latexmk", "-pdf", tex_name]
        passes = 1
    else:
        cmd = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex_name]
        passes = 2  # 2 pasadas para resolver la toc y referencias cruzadas

    try:
        for _ in range(passes):
            res = subprocess.run(
                cmd, cwd=cwd, stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=300,
            )
    except subprocess.TimeoutExpired:
        return False, "⚠ Compilación excedió el tiempo máximo (300 s)."
    except FileNotFoundError:
        return False, f"⚠ {backend} no está disponible en el PATH."

    if res.returncode != 0:
        tail = (res.stderr or res.stdout or "").strip()[-800:]
        if tail:
            tail = "\n" + tail
        return False, f"⚠ Compilación fallida ({detail}).{tail}"

    return True, f"📄 {Path(tex_path).stem}.pdf compilado ({detail})"
