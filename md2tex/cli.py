import sys
from datetime import datetime
from pathlib import Path

import questionary

from .converter import parse, _render_block
from .deps import compile_pdf, ensure_compile_available, status_report
from .image_handler import handle_images
from .template import build_latex


def find_md_files() -> list[Path]:
    return sorted(Path(".").resolve().glob("*.md"))


def main():
    print("╔══════════════════════════════════════╗")
    print("║  md2tex — Markdown a LaTeX           ║")
    print("╚══════════════════════════════════════╝")
    print()

    from .environment.checker import EnvironmentChecker
    from .environment.validator import EnvironmentValidator

    print("Estado del entorno:")
    print("  " + status_report().replace("\n", "\n  "))
    validation = EnvironmentValidator.validate()
    if validation["all_ok"]:
        print(f"  🟢 Entorno listo — Motor: {validation['backend'] or 'Ninguno'}")
    else:
        missing = validation.get("missing_tools", [])
        mpkgs = validation.get("missing_packages", [])
        if missing:
            print(f"  🟡 Herramientas faltantes: {', '.join(missing)}")
        if mpkgs:
            print(f"  🟡 Paquetes faltantes: {', '.join(mpkgs)}")
    print()

    choice = questionary.select(
        "¿Qué desea hacer?",
        choices=[
            "Convertir Markdown a LaTeX",
            "Diagnóstico del entorno",
            "Reparar entorno",
            "Salir",
        ],
    ).ask()

    if choice == "Diagnóstico del entorno":
        _run_diagnosis()
        sys.exit(0)
    elif choice == "Reparar entorno":
        _run_repair()
        sys.exit(0)
    elif choice == "Salir":
        print("¡Hasta luego!")
        sys.exit(0)

    print()
    md_files = find_md_files()

    choices = [str(f) for f in md_files]
    choices.append("Especificar otra ruta...")

    selected = questionary.select(
        "Selecciona el archivo Markdown:",
        choices=choices,
    ).ask()

    if selected is None:
        print("Operación cancelada.")
        sys.exit(1)

    if selected == "Especificar otra ruta...":
        md_path_str = questionary.path("Ruta del archivo .md:").ask()
        if not md_path_str:
            print("Operación cancelada.")
            sys.exit(1)
        md_path = Path(md_path_str).resolve()
    else:
        md_path = Path(selected).resolve()

    if not md_path.is_file():
        print(f"Error: no se encontró el archivo {md_path}")
        sys.exit(1)

    title = questionary.text("Título del informe:", default=md_path.stem).ask()
    author = questionary.text("Autor:", default="").ask()
    compile_choice = questionary.confirm(
        "¿Compilar con latexmk después de generar?",
        default=True,
    ).ask()

    print()
    print(f"  Procesando: {md_path.name}")

    md_text = md_path.read_text(encoding="utf-8")
    tokens, fn_map = parse(md_text)

    out_dir = Path(".").resolve()
    image_map = handle_images(tokens, out_dir)

    if image_map:
        print(f"  Imágenes copiadas: {len(image_map)}")

    content = _render_block(tokens, image_map, fn_map)

    date_str = datetime.now().strftime("%Y-%m-%d")
    latex = build_latex(
        title=title,
        author=author if author else title,
        date=date_str,
        content=content,
    )

    out_path = out_dir / f"{md_path.stem}.tex"
    out_path.write_text(latex, encoding="utf-8")
    print(f"  Generado: {out_path.name}")

    if compile_choice:
        env_msg = ensure_compile_available()
        if env_msg:
            print("  No se pudo compilar: faltan dependencias.")
            print(env_msg)
        else:
            print("  Estado del entorno:")
            print("    " + status_report().replace("\n", "\n    "))
            ok, cmsg = compile_pdf(out_path, out_dir)
            print(f"  {cmsg}")

    print()
    print("¡Listo!")


def _run_diagnosis():
    from .environment.report import EnvironmentReporter
    report = EnvironmentReporter.generate_report()
    print(report)
    save = questionary.confirm("¿Guardar reporte a archivo?", default=False).ask()
    if save:
        path = questionary.path(
            "Ruta del archivo:", default="md2tex-diagnostico.txt"
        ).ask()
        if path:
            from pathlib import Path
            EnvironmentReporter.generate_report(Path(path))
            print(f"  Reporte guardado: {Path(path).name}")


def _run_repair():
    from .environment.repair import EnvironmentRepairer
    from .environment.installer import DependencyInstaller

    print("Reparando entorno...")
    repairer = EnvironmentRepairer()
    success, message, actions = repairer.repair()
    print(f"  {message}")
    for a in actions:
        print(f"  · {a}")

    installer = DependencyInstaller()
    ok, msg, install_actions = installer.install_all_needed()
    print(f"  {msg}")
    for a in install_actions:
        print(f"  · {a}")
