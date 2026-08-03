"""Barra de menú de md2tex.

Construye el menú de la aplicación usando únicamente widgets oficiales de
``tkinter`` (no depende de ``CTkMenuBar``, que no existe en la API oficial de
CustomTkinter). Un fallo aquí no debe impedir que la aplicación arranque.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from tkinter import Menu as TkMenu

logger = logging.getLogger("md2tex.ui.menu")

LOG_FILE = "md2tex-ui.log"


def setup_menu(app) -> bool:
    """Crea la barra de menú de la aplicación.

    Devuelve ``True`` si el menú se construyó correctamente y ``False`` si
    falló (en cuyo caso el error queda registrado en el log).
    """
    try:
        menubar = TkMenu(app)
        app.configure(menu=menubar)

        tools_menu = TkMenu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(
            label="Diagnóstico del entorno",
            command=getattr(app, "_run_diagnosis", None),
        )
        tools_menu.add_command(
            label="Reparar entorno",
            command=getattr(app, "_run_repair", None),
        )
        tools_menu.add_separator()
        tools_menu.add_command(
            label="Salir",
            command=getattr(app, "_on_close", None),
        )

        return True
    except Exception as exc:  # pragma: no cover - defensivo
        _log_error("setup_menu", exc)
        return False


def _log_error(context: str, exc: Exception) -> None:
    """Registra el error completo en consola y en el log en disco."""
    message = (
        f"Error al inicializar la interfaz ({context}): "
        f"{type(exc).__name__}: {exc}"
    )
    logger.error(message)
    try:
        with Path(LOG_FILE).open("a", encoding="utf-8") as fh:
            fh.write(f"[{context}] {message}\n")
    except OSError:
        pass


def platform_menu_style() -> str:
    """Devuelve el estilo de menú recomendado para el SO actual."""
    if sys.platform == "darwin":
        return "macos"
    if sys.platform == "win32":
        return "windows"
    return "linux"
