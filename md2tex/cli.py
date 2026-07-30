import subprocess
import sys
from datetime import datetime
from pathlib import Path

import questionary

from .converter import parse, _render_block
from .image_handler import handle_images
from .template import build_latex


def find_md_files():
    return sorted(Path(".").glob("*.md"))


def has_latexmk():
    try:
        result = subprocess.run(
            ["latexmk", "--version"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def main():
    print("╔══════════════════════════════════════╗")
    print("║  md2tex — Markdown a LaTeX           ║")
    print("╚══════════════════════════════════════╝")
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

    has_latexmk_bin = has_latexmk()
    if compile_choice and has_latexmk_bin:
        print(f"  Compilando con latexmk...")
        result = subprocess.run(
            ["latexmk", "-pdf", str(out_path)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            print(f"  PDF generado: {out_path.stem}.pdf")
        else:
            print("  Error en compilación. Revisa el archivo .log")
    elif compile_choice and not has_latexmk_bin:
        print("  latexmk no está disponible. Compila manualmente con:")
        print(f"  $ latexmk -pdf {out_path.name}")

    print()
    print("¡Listo!")
