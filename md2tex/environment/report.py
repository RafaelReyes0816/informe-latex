from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .checker import EnvironmentChecker


class EnvironmentReporter:
    @classmethod
    def generate_report(cls, output_path: Path | str | None = None) -> str:
        report = cls._build_report()
        if output_path:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(report, encoding="utf-8")
        return report

    @classmethod
    def _build_report(cls) -> str:
        lines = []
        check_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"Reporte de Diagnóstico de md2tex")
        lines.append(f"Generado: {check_time}")
        lines.append(f"Versión: {cls._get_version()}")
        lines.append("")

        lines.append("=" * 50)
        lines.append("SISTEMA")
        lines.append("=" * 50)
        os_info = EnvironmentChecker.detect_os()
        for key, value in os_info.items():
            lines.append(f"  {key}: {value}")
        lines.append("")

        lines.append("=" * 50)
        lines.append("COMPILADORES")
        lines.append("=" * 50)
        compilers = EnvironmentChecker.available_compilers()
        if compilers:
            for c in compilers:
                version = EnvironmentChecker.find_executable(c)
                ver_str = ""
                if version:
                    v = EnvironmentChecker.get_version(c)
                    if v:
                        ver_str = f" ({v})"
                lines.append(f"  ✓ {c}{ver_str}")
        else:
            lines.append("  ✗ No se encontraron compiladores")
        backend, detail = EnvironmentChecker.preferred_backend()
        lines.append(f"  Motor principal: {backend or 'Ninguno'} ({detail})")
        lines.append("")

        lines.append("=" * 50)
        lines.append("HERRAMIENTAS")
        lines.append("=" * 50)
        lines.append(EnvironmentChecker.status_report())
        lines.append("")

        lines.append("=" * 50)
        lines.append("PAQUETES LaTeX")
        lines.append("=" * 50)
        lines.append(EnvironmentChecker.packages_report())
        lines.append("")

        lines.append("=" * 50)
        lines.append("CONFIGURACIÓN")
        lines.append("=" * 50)
        disk_ok, disk_msg = EnvironmentChecker.check_disk_space()
        disk_mark = "✓" if disk_ok else "✗"
        lines.append(f"  {disk_mark} Espacio en disco: {disk_msg}")
        perms = EnvironmentChecker.check_permissions()
        for k, v in perms.items():
            mark = "✓" if v else "✗"
            lines.append(f"  {mark} {k}")
        lines.append("")

        lines.append("=" * 50)
        lines.append("VALIDACIÓN DE PLANTILLAS")
        lines.append("=" * 50)
        from .validator import EnvironmentValidator
        res = EnvironmentValidator.validate_resources()
        lines.append(f"  Directorio: {res.get('templates_dir', 'N/A')}")
        lines.append(f"  Existe: {'Sí' if res.get('templates_dir_exists') else 'No'}")
        lines.append(f"  Plantillas: {res.get('templates_available', [])}")
        lines.append(f"  Plantilla por defecto válida: {'Sí' if res.get('default_template_valid') else 'No'}")
        lines.append("")

        lines.append("=" * 50)
        lines.append("COMPILACIÓN DE PRUEBA")
        lines.append("=" * 50)
        ok, msg = cls._test_compilation()
        mark = "✓" if ok else "✗"
        lines.append(f"  {mark} {msg}")
        lines.append("")

        lines.append("=" * 50)
        lines.append("RESULTADO FINAL")
        lines.append("=" * 50)
        validation = EnvironmentValidator.validate()
        if validation["all_ok"]:
            lines.append("  🟢 Entorno completamente funcional")
        else:
            lines.append("  🟡 Entorno con problemas")
            if validation["missing_tools"]:
                lines.append(f"  Herramientas faltantes: {validation['missing_tools']}")
            if validation["missing_packages"]:
                lines.append(f"  Paquetes faltantes: {validation['missing_packages']}")
            if not validation["compile_ok"]:
                lines.append("  La compilación falló")
            if not disk_ok:
                lines.append("  Espacio en disco insuficiente")

        return "\n".join(lines)

    @staticmethod
    def _test_compilation() -> tuple[bool, str]:
        from .compiler import LatexCompiler
        return LatexCompiler.diagnose_compile()

    @staticmethod
    def _get_version() -> str:
        try:
            from md2tex import __version__
            return __version__
        except ImportError:
            return "desconocida"
