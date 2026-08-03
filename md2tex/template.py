import sys
from pathlib import Path


def _templates_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "templates"
    return Path(__file__).resolve().parent.parent / "templates"


TEMPLATES_DIR = _templates_dir()

BUILTIN = r"""\documentclass[12pt,a4paper]{article}

\usepackage{iftex}

\ifPDFTeX
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
\else
  \usepackage{fontspec}
\fi

\usepackage[spanish]{babel}

\usepackage{amsmath,amssymb}

\usepackage{graphicx}
\graphicspath{{figures/}}

\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}

\usepackage{booktabs}
\usepackage{array}

\usepackage{xcolor}
\usepackage{listings}
\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  frame=single,
  numbers=left,
  numberstyle=\tiny,
}

\usepackage[top=2.5cm, bottom=2.5cm, left=3cm, right=2.5cm]{geometry}

\usepackage{setspace}
\onehalfspacing

\title{{TITLE}}
\author{{AUTHOR}}
\date{{DATE}}

\begin{document}

\maketitle
\tableofcontents
\newpage

{CONTENT}

\end{document}
"""


def list_templates() -> list:
    if not TEMPLATES_DIR.is_dir():
        return []
    return sorted(
        f.stem for f in TEMPLATES_DIR.iterdir() if f.suffix == ".tex"
    ) or ["default"]


def load_template(name: str) -> str:
    stem = name.replace(".tex", "")
    for candidate in [f"{stem}.tex", name]:
        path = TEMPLATES_DIR / candidate
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return BUILTIN


def apply_template(
    template_text: str,
    title: str,
    author: str,
    date: str,
    content: str,
) -> str:
    result = template_text.replace("{TITLE}", title)
    result = result.replace("{AUTHOR}", author)
    result = result.replace("{DATE}", date)
    result = result.replace("{CONTENT}", content)
    return result


def build_latex(
    title: str,
    author: str,
    date: str,
    content: str,
    template_name: str = "default",
) -> str:
    template = load_template(template_name)
    return apply_template(template, title, author, date, content)


def build_latex_multi(
    title: str,
    author: str,
    date: str,
    file_stems: list,
    template_name: str = "default",
) -> str:
    content = "\n".join(f"\\include{{{stem}}}" for stem in file_stems)
    return build_latex(title, author, date, content, template_name)
