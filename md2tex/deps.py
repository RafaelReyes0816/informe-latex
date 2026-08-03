"""Detección, reporte y compilación de PDFs de md2tex.

Esta versión sirve como capa de compatibilidad. La funcionalidad principal
se ha migrado al paquete ``md2tex.environment``. Este módulo mantiene la API
anterior para que cli.py y gui.py funcionen sin cambios.
"""

from __future__ import annotations

from .environment.checker import (
    EnvironmentChecker,
    _HINTS,
    _HUMAN_TOOL_NAMES,
    _PACKAGES,
    _TOOLS,
)
from .environment.compiler import (
    LatexCompiler,
    COMPILER_ORDER,
    compile_pdf,
)

# --- API de módulo (compatibilidad con cli.py / gui.py) ---
which = EnvironmentChecker.which
latex_dependencies = EnvironmentChecker.latex_dependencies
status_report = EnvironmentChecker.status_report
preferred_backend = EnvironmentChecker.preferred_backend
missing_dependencies = EnvironmentChecker.missing
ensure_latex_dependencies = EnvironmentChecker.ensure_compile_available
ensure_compile_available = EnvironmentChecker.ensure_compile_available

try:
    from md2tex import __version__
except ImportError:
    __version__ = "1.0.0"
