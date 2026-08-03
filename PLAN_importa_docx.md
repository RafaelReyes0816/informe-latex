# Plan: Importación de documentos DOCX → Markdown (postergado)

Status: **Postergado / Futuro** — planificación para una versión posterior.
Base: conversación sobre dependencias de instaladores y mejora del flujo de trabajo.

## Objetivo

Ampliar el flujo actual `Markdown → LaTeX → PDF` con una entrada nueva:

```
DOCX ──► md2tex ──► Markdown ──► (flujo actual) ──► LaTeX ──► PDF
```

Permitir que el usuario importe un documento DOCX y genere, de forma
automática, el archivo Markdown (sin perder imágenes) para después
convertirlo a LaTeX como ya ocurre hoy.

## Decisiones acordadas

1. **Motor DOCX → Markdown:** **Pandoc** como binario externo (prerrequisito
   de sistema), al igual que `latexmk`. No se agregan dependencias Python.
2. **Alcance de esta versión:** **solo DOCX**. PDF se posterga.
3. **Integración UI/CLI:** botón "Importar DOCX" en la GUI y opción en el
   menú interactivo de la CLI.

## Arquitectura propuesta

Nuevo paquete dentro de `md2tex/`:

```
md2tex/
├── converters/
│   ├── __init__.py            # registry + dispatch por extensión
│   ├── base_converter.py      # ABC + helpers (has_pandoc, etc.)
│   ├── docx_converter.py      # DOCX → Markdown (Pandoc)
│   └── pdf_converter.py       # (placeholder, futuro)
```

### `base_converter.py`

```python
from pathlib import Path

def has_pandoc() -> bool: ...      # True si `pandoc` está en PATH
def pandoc_install_hint() -> str:  # instrucciones de instalación por SO

class BaseConverter:
    extensions: tuple[str, ...]    # ej. (".docx",)

    def convert(self, src: Path, out_dir: Path) -> Path:
        """Convierte `src` a un .md dentro de `out_dir` y devuelve su path."""
        raise NotImplementedError
```

### `docx_converter.py`

```python
class DocxConverter(BaseConverter):
    extensions = (".docx",)

    def convert(self, src, out_dir):
        if not has_pandoc():
            raise RuntimeError(pandoc_install_hint())
        stem = src.stem
        md_path = out_dir / f"{stem}.md"
        media_dir = out_dir / "images"          # <-- normalizar a "images/"
        subprocess.run(
            ["pandoc", str(src), "-o", str(md_path),
             f"--extract-media={media_dir}"],
            check=True,
        )
        self._normalize_media_references(md_path, media_dir)
        return md_path

    def _normalize_media_references(self, md_path, media_dir):
        """
        Pandoc (dependiendo de la versión) escribe imágenes dentro de
        `media_dir/media/` y referencia `media/imagen.png`.
        Se normaliza el Markdown para que referencie `<out_dir>/images/...`.

        Pasos:
        1. Detectar el subdirectorio real donde pandoc dejó las imágenes
           (p. ej. `images/media/`).
        2. Si existe, levantar un nivel: copiar/mover `images/media/*` a
           `images/` y reescribir las referencias `media/` → `` (o
           ajustar a `images/` según convenga).
        3. Garantizar que `![texto](images/imagen.png)` apunte a un archivo
           efectivamente presente al lado del .md.

        Pendiente de verificación durante implementación (la ruta exacta
        depende de la versión de pandoc instalada).
        """
```

> Nota de verificación: `pandoc --extract-media=DIR` por defecto produce
> `DIR/media/<hash>.*` y referencias `media/...`. Confirmar en CI y en la
> máquina del desarrollador.

### `converters/__init__.py`

```python
from .docx_converter import DocxConverter
# from .pdf_converter import PdfConverter  # futuro

def get_converter(path: Path) -> BaseConverter | None:
    ext = path.suffix.lower()
    for cls in (DocxConverter,):
        if ext in cls.extensions:
            return cls()
    return None
```

## Mejora de `image_handler.py` (requisito)

Bug actual: `handle_images()` resuelve URLs de imagen relative al **CWD**,
pero el Markdown importado referencia imágenes relativas a su propio
directorio (`images/foo.png`).

Cambio:

```python
def handle_images(tokens, output_dir=".", base_dir=None):
    """
    base_dir: directorio del archivo Markdown origen. Si se pasa, las
    referencias relativas se resuelven contra él antes de copiarlas a
    figures/. Si la imagen ya está en output_dir/figures, se mantiene.
    """
    ...
    src = Path(url)
    if not src.is_file() and base_dir is not None:
        src = Path(base_dir) / url
    ...
```

Llamados actualizados en `gui.py` y `cli.py` → pasar `md_path.parent`.

## Integración GUI (`gui.py`)

- Nuevo botón **"📥 Importar DOCX"** en `ConfigPanel`, al lado de "+ Añadir".
- Al click:
  1. File dialog con filtro `*.docx`.
  2. `DocxConverter().convert(src, out_dir=Path(out_dir_var).resolve())`.
  3. `file_list.add_file(md_path)`.
  4. `preview_panel.show_markdown(md_path)`.
- Si falta Pandoc: `messagebox.showerror` con instrucciones de instalación.

## Integración CLI (`cli.py`)

- Menu/option: **"Importar documento DOCX"**.
- Preguntar ruta del `.docx`.
- Convertir con `DocxConverter`.
- Añadir el `.md` generado al listado de candidatos y proseguir con el
  flujo existente.
- Si falta Pandoc: imprimir instrucciones y retornar.

## Dependencias y empaquetado

- `requirements.txt` / `pyproject.toml`: **sin cambios** (Pandoc es binario
  externo).
- `build.py`: **sin cambios**.
- Instaladores:
  - Linux `.deb` (`installer/linux/create-deb.sh`): añadir `pandoc` al
    campo `Depends:`.
  - Windows / macOS: documentar + detección en *runtime* con instrucciones.
- Documentación (`README.md`, `AGENTS.md`): agregar Pandoc como
  prerrequisito y el nuevo flujo `DOCX → MD → LaTeX → PDF`.

## Pruebas

- Fixture: generar un `.docx` con `python-docx` (una section, un párrafo y
  una imagen insertada) → usarlo en tests.
- Test: convertir y verificar
  1. el `.md` se crea,
  2. la imagen se extrajo a `images/`,
  3. la referencia `![...]` apunta a un archivo existente,
  4. `handle_images(..., base_dir=...)` copia la imagen a `figures/`.
- CI: instalar `pandoc` en los runners (Linux `apt`, macOS `brew`,
  Windows `winget install pandoc`).

## Riesgos / limitaciones

- Pandoc extrae imágenes a `media/` (variable según versión) → requiere
  normalización (ver `_normalize_media_references`).
- Fidelidad DOCX→MD: limitado con documentos muy complejos
  (notas al pie con estilos especiales, tablas anidadas, etc.).
- Pandoc es un prerrequisito adicional, idéntico al trato actual de `latexmk`.

## Orden de implementación sugerido

1. `converters/base_converter.py` + `docx_converter.py`.
2. Mejora de `image_handler.py` (`base_dir`).
3. Integración GUI.
4. Integración CLI.
5. `.deb` Depends (`pandoc`) + docs (README/AGENTS).
6. Tests + CI.
7. Bump versión (`0.3.0`) y release.
