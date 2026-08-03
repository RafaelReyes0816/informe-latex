# md2tex

Conversor de Markdown a LaTeX con interfaz gráfica (GUI) y de línea de comandos (CLI). Convierte archivos `.md` en documentos `.tex` compilables y, si tienes instalado LaTeX, genera el PDF directamente.

## ¿Qué hace?

El flujo es sencillo:

```text
Archivos .md ──► md2tex ──► Documento .tex ──► latexmk ──► PDF
```

1. Seleccionas uno o varios archivos Markdown.
2. Configuras título, autor, template y directorio de salida.
3. md2tex convierte el contenido (tablas, listas, código, imágenes, citas, notas al pie, matemáticas) a LaTeX.
4. Si activas la compilación, `latexmk` genera el PDF final.

Puedes generar un único documento o varios capítulos que se integran en un documento principal con `\include{}`.

## Características

- **GUI** (customtkinter) con panel de previsualización de Markdown y LaTeX.
- **CLI** interactivo.
- Mapeo completo de Markdown → LaTeX: encabezados, tablas, listas, bloques de código con resaltado, imágenes, `\cite{}`, notas al pie y fórmulas matemáticas.
- Copiado automático de imágenes a `figures/`.
- Templates personalizables (`templates/`) con placeholders `{TITLE}`, `{AUTHOR}`, `{DATE}`, `{CONTENT}`.
- Guardado de configuración de proyecto (`.md2tex_project.json`).
- Instaladores para Linux (`.deb`), macOS (`.dmg`) y Windows (`.exe`).
- El instalador de Windows detecta si falta LaTeX y puede descargar e instalar MiKTeX automáticamente.

## Prerrequisitos del sistema

- **Python ≥ 3.10** con tkinter (en Linux: `sudo apt install python3-tk`).
- **LaTeX** para compilar el PDF:
  - Linux: `sudo apt install texlive-latex-base texlive-latex-extra`
  - macOS: MacTeX (`brew install --cask mactex`)
  - Windows: MiKTeX. El instalador de md2tex detecta si no está instalado y ofrece descargarlo e instalarlo automáticamente (~150 MB); si lo rechazas, puedes instalarlo luego desde https://miktex.org/download
- **latexmk** (incluido con LaTeX; en Windows MiKTeX: `mpm --install=latexmk`).
- **Perl** (necesario para latexmk en Windows: instale Strawberry Perl desde https://strawberryperl.com).
- **Perl** no es obligatorio en Linux/macOS (viene incluido).

> **Nota:** si no tienes LaTeX, el programa sigue funcionando: convierte Markdown a `.tex`. Solo la generación del PDF requiere LaTeX. En la GUI puedes desmarcar "Compilar con latexmk".

## Instalación desde código

```bash
python3 -m venv .venv
source .venv/bin/activate          # Linux/macOS  |  .venv\Scripts\activate  (Windows)
pip install -r requirements.txt
```

## Uso

### GUI

```bash
python -m md2tex
```

### CLI

```bash
python -m md2tex --cli
```

## Mapeo Markdown → LaTeX soportado

| Markdown | LaTeX |
|---|---|
| `#`–`#####` | `\section{}`–`\subparagraph{}` |
| `**negrita**` / `*cursiva*` | `\textbf{}` / `\textit{}` |
| `` `código` `` | `\texttt{}` |
| `` ```lenguaje `` | `\begin{lstlisting}[language=...]` |
| `[texto](url)` | `\href{url}{texto}` |
| `![alt](img.png)` | `figure` + `\includegraphics` |
| Tablas | `tabular` + `booktabs` |
| `-` / `1.` listas | `itemize` / `enumerate` |
| `$...$` / `$$...$$` | Pasa tal cual (LaTeX válido) |
| `[^fn]:` | `\footnote{}` |
| `[@key]` | `\cite{key}` (gestión de `.bib` manual) |
| `---` | `\hrule` |

## Build (desarrollo)

```bash
latexmk -pdf main.tex   # compilar documento LaTeX
```

## Instaladores

```bash
python build.py binaries   # binarios GUI + CLI (PyInstaller)
python build.py installer  # .deb (Linux) / .dmg (macOS) / .exe (Windows)
```

## Release

Los tags `v*` disparan GitHub Actions que construyen los instaladores de los tres SO y publican una Release:

| Plataforma | Formato |
|---|---|
| Linux | `.deb` |
| macOS | `.dmg` |
| Windows | `.exe` (Inno Setup) |

```bash
git tag -a v0.2.3 -m "v0.2.3"
git push origin v0.2.3
```

Bump de versión en `md2tex/__init__.py` y `pyproject.toml` antes de etiquetar.

## Licencia

MIT
