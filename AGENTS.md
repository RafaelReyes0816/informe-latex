# AGENTS.md — informe-latex

LaTeX project for reports and research documents.

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

## Common pitfalls

- Do **not** commit build artifacts (`*.aux`, `*.log`, `*.out`, `*.toc`, `*.fdb_latexmk`, `*.fls`, `*.bbl`, `*.bcf`, `*.blg`, `*.run.xml`, `_minted-*`). Add to `.gitignore`.
- If bibliography does not update, run `latexmk -pdf` (not just `pdflatex`) — it handles `biber`/`bibtex` automatically.
- If errors are cryptic, check the `.log` file for the real message.
