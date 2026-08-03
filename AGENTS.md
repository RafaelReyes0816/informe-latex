# AGENTS.md — informe-latex

LaTeX project for reports and research documents.

## Prerrequisitos del sistema

- **Python ≥ 3.10** con tkinter (en Linux: `sudo apt install python3-tk`)
- **LaTeX** (basta un motor): `sudo apt install texlive-latex-base texlive-xetex` (Linux), MacTeX (macOS), MiKTeX (Windows)
- **latexmk** y **Perl** solo para el modo avanzado `latexmk`; **opcionales**, md2tex compila con `xelatex`/`lualatex`/`pdflatex` sin Perl. El instalador de Windows ya no instala Strawberry Perl.

## Build

```bash
latexmk -pdf                    # full build
latexmk -pdf main.tex           # single file
latexmk -c                      # clean intermediates (keep PDF)
latexmk -C                      # clean everything
```

`latexmk` is the only build tool — no Makefile. It re-runs `pdflatex`/`biber`/`makeindex` as many times as needed automatically.

## Conventions

- Main entrypoint: `main.tex`.
- Figures in `figures/` or `img/`, bibliography in `bib/` or `references.bib`, chapters in `capitulos/` or `secciones/`.
- Name chapters descriptively (e.g., `introduccion.tex`, `metodologia.tex`) and `\input` or `\include` them from `main.tex`.
- Use `\input` for short fragments, `\include` for standalone chapter files (each gets its own `.aux`).

## md2tex — Markdown → LaTeX converter

Interactive tool (GUI + CLI) that converts `.md` files into compilable LaTeX.

```bash
pip install -r requirements.txt   # one-time setup
python -m md2tex                  # launches GUI
python -m md2tex --cli            # terminal interactive menu
```

### Supported Markdown → LaTeX mapping

| Markdown | LaTeX | Notes |
|---|---|---|
| `#`–`#####` | `\section{}`–`\subparagraph{}` | |
| `**bold**` / `*italic*` | `\textbf{}` / `\textit{}` | |
| `` `code` `` | `\texttt{}` | |
| `` ```lang `` | `\begin{lstlisting}[language=lang]` | |
| `[text](url)` | `\href{url}{text}` | |
| `![alt](img.png)` | `figure` + `\includegraphics` + `\caption` | Images auto-copied to `figures/` |
| Tables | `tabular` + `booktabs` | Headers in `\textbf{}` |
| `-` / `1.` lists | `itemize` / `enumerate` | |
| `$...$` / `$$...$$` | pass through | Already valid LaTeX |
| `[^fn]:` | `\footnote{}` | |
| `[@key]` | `\cite{key}` | `[@k1; @k2]` → `\cite{k1,k2}` |
| `---` | `\hrule` | |

### Templates

- Built-in: `default` (article, graphicx, booktabs, listings, hyperref).
- Custom templates in `templates/` dir (`{TITLE}`, `{AUTHOR}`, `{DATE}`, `{CONTENT}` placeholders).
- Multiple `.md` files generate `\include{}`-based main document + per-file `.tex`.

### Caveats

- Images in markdown `![](ruta)` must exist on disk; they are copied to `figures/`
- Code blocks with language use `lstlisting` (requires `-shell-escape` if using `minted`)
- No `biber`/`bibliography` processing yet; `\cite{}` is emitted but `.bib` must be managed manually
- GUI requires a display server (X11/Wayland). Headless → use `--cli`.

## Releases

Tag pushes (`v*`) trigger GitHub Actions to build platform installers via PyInstaller + Inno Setup / DMG / dpkg-deb.

```bash
make VERSION=0.2.0 tag    # create + push tag
# or manually:
git tag -a v0.2.0 -m "v0.2.0"
git push origin v0.2.0
```

The workflow at `.github/workflows/release.yml` builds and creates a GitHub Release with:

| Platform | Format | File name |
|---|---|---|
| Linux | `.deb` | `md2tex_{version}_amd64.deb` |
| macOS | `.dmg` | `md2tex-{version}.dmg` |
| Windows | `.exe` (Inno Setup) | `md2tex-setup-v{version}.exe` |

Bump version in `md2tex/__init__.py` and `pyproject.toml` before tagging.

## PDF compilation (runtime)

md2tex elige el motor de compilación con `md2tex/environment/checker.py::EnvironmentChecker.resolve_backend(engine)`:

1. **Modo automático** (`auto`, por defecto): primer motor disponible de `COMPILER_ORDER = ("xelatex", "lualatex", "pdflatex")`. Si no hay ninguno, último recurso `latexmk + perl`.
2. **Modo avanzado** (`latexmk`): requiere `latexmk` y `perl`; no son obligatorios para compilar.
3. Ninguno → mensaje amigable con instrucciones de instalación por SO.

`compile_pdf(tex_path, cwd, log_dir, engine="auto")` ejecuta **2 pasadas** con cualquier motor (1 para `latexmk`, que se resuelve solo). En Windows "prepara" MiKTeX corriendo `initexmf --update-fndb` y `[MPM]AutoInstall=1` antes de compilar, y reintenta con `mpm --update-db` si aparece el típico aviso de primera ejecución *"So far, you have not checked for MiKTeX updates"*.

## Environment Management (v1.1.0)

md2tex incluye un sistema de gestión de dependencias multi-plataforma en `md2tex/environment/`:

- `base.py` — clase base `EnvironmentBase` con detección del sistema, herramientas y permisos.
- `checker.py` — `EnvironmentChecker`: detección de compiladores, versiones, paquetes LaTeX (vía `kpsewhich`).
- `compiler.py` — `LatexCompiler`: compila con el motor seleccionado (`auto` → `xelatex → lualatex → pdflatex`; `latexmk` avanzado), 2 pasadas.
- `validator.py` — `EnvironmentValidator`: validación completa del entorno antes de compilar.
- `report.py` — `EnvironmentReporter`: genera informes de diagnóstico detallados.
- `repair.py` — `EnvironmentRepairer`: corrige PATH, MiKTeX, paquetes y limpia temporales.
- `installer.py` — `DependencyInstaller`: instala dependencias (MiKTeX en Windows, apt/brew en Linux/macOS).
- `windows.py`, `linux.py`, `macos.py` — gestión específica por SO.

### Diagnóstico y reparación

Desde la GUI: **Herramientas → Diagnóstico del entorno / Reparar entorno**.
Desde CLI: selecciona la opción al iniciar.

`md2tex/deps.py` mantiene compatibilidad como capa delgada que delega al paquete `environment/`.

## Common pitfalls

- Do **not** commit build artifacts (`*.aux`, `*.log`, `*.out`, `*.toc`, `*.fdb_latexmk`, `*.fls`, `*.bbl`, `*.bcf`, `*.blg`, `*.run.xml`, `_minted-*`). Add to `.gitignore`.
- If bibliography does not update, run `latexmk -pdf` (not just `pdflatex`) — it handles `biber`/`bibtex` automatically.
- If errors are cryptic, check the `.log` file for the real message.
