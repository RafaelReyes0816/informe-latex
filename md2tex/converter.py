import re

import mistune
from mistune.plugins.table import table as plugin_table
from mistune.plugins.footnotes import footnotes as plugin_fn

_parser = mistune.Markdown(renderer=None)
_parser.use(plugin_table)
_parser.use(plugin_fn)


def preprocess_citations(text: str) -> str:
    return re.sub(
        r"\[@([^\]]+)\]",
        lambda m: "\\cite{" + m.group(1).replace(";", ",").replace(" ", "") + "}",
        text,
    )


def parse(text: str) -> tuple:
    text = preprocess_citations(text)
    tokens, _state = _parser.parse(text)

    footnote_map = {}
    remaining = []
    for token in tokens:
        if token.get("type") == "footnotes":
            for fn in token.get("children", []):
                key = str(fn.get("attrs", {}).get("key", ""))
                content = _render_block(fn.get("children", []))
                footnote_map[key] = content.strip()
        else:
            remaining.append(token)

    return remaining, footnote_map


def md_to_latex(text: str, image_map: dict = None) -> str:
    tokens, fn_map = parse(text)
    return _render_block(tokens, image_map, fn_map)


def escape_tex(text: str) -> str:
    chars = str.maketrans({
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "#": r"\#",
        "%": r"\%",
        "&": r"\&",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    })
    return text.translate(chars)


def render_inline(tokens, image_map=None, fn_map=None):
    if image_map is None:
        image_map = {}
    if fn_map is None:
        fn_map = {}
    out = []
    for t in tokens:
        out.append(_render_inline_token(t, image_map, fn_map))
    return "".join(out)


def _render_inline_token(t, image_map, fn_map):
    type_ = t.get("type", "")

    if type_ == "text":
        return t.get("raw", "")
    if type_ == "emphasis":
        return f"\\textit{{{render_inline(t.get('children', []), image_map, fn_map)}}}"
    if type_ == "strong":
        return f"\\textbf{{{render_inline(t.get('children', []), image_map, fn_map)}}}"
    if type_ == "codespan":
        return f"\\texttt{{{escape_tex(t.get('raw', ''))}}}"
    if type_ == "link":
        url = t.get("attrs", {}).get("url", "")
        text = render_inline(t.get("children", []), image_map, fn_map)
        return f"\\href{{{url}}}{{{text}}}"
    if type_ == "image":
        url = t.get("attrs", {}).get("url", "")
        alt = t.get("attrs", {}).get("alt", "")
        path = image_map.get(url, url)
        return (
            f"\\begin{{figure}}[htbp]\n"
            f"\\centering\n"
            f"\\includegraphics[width=\\textwidth]{{{path}}}\n"
            f"\\caption{{{alt}}}\n"
            f"\\end{{figure}}"
        )
    if type_ == "footnote_ref":
        key = str(t.get("attrs", {}).get("index", ""))
        text = fn_map.get(key, "")
        return f"\\footnote{{{text}}}"
    if type_ == "softbreak":
        return "\n"
    if type_ == "linebreak":
        return "\\\\\n"
    if type_ == "inline_html":
        return t.get("raw", "")
    return ""


def render_inline_compact(tokens, image_map=None, fn_map=None):
    text = render_inline(tokens, image_map, fn_map)
    return text.replace("\n", " ")


def _render_block(tokens, image_map=None, fn_map=None):
    if image_map is None:
        image_map = {}
    if fn_map is None:
        fn_map = {}
    out = []
    for t in tokens:
        latex = _render_block_token(t, image_map, fn_map)
        if latex:
            out.append(latex)
    return "\n\n".join(out)


def _render_block_token(t, image_map, fn_map):
    type_ = t.get("type", "")

    if type_ == "heading":
        level = t.get("attrs", {}).get("level", 1)
        text = render_inline_compact(t.get("children", []), image_map, fn_map)
        cmd = {1: "section", 2: "subsection", 3: "subsubsection",
               4: "paragraph", 5: "subparagraph"}
        return f"\\{cmd.get(level, 'textbf')}{{{text}}}"

    if type_ == "paragraph":
        text = render_inline(t.get("children", []), image_map, fn_map)
        return text if text.strip() else ""

    if type_ == "block_text":
        text = render_inline(t.get("children", []), image_map, fn_map)
        return text if text.strip() else ""

    if type_ == "block_quote":
        inner = _render_block(t.get("children", []), image_map, fn_map)
        return f"\\begin{{quote}}\n{inner}\n\\end{{quote}}"

    if type_ == "list":
        ordered = t.get("attrs", {}).get("ordered", False)
        env = "enumerate" if ordered else "itemize"
        items = []
        for child in t.get("children", []):
            if child.get("type") == "list_item":
                item_text = _render_block(child.get("children", []), image_map, fn_map)
                items.append(f"\\item {item_text}")
        return f"\\begin{{{env}}}\n" + "\n".join(items) + f"\n\\end{{{env}}}"

    if type_ == "block_code":
        lang = t.get("attrs", {}).get("lang", "") or t.get("attrs", {}).get("info", "")
        code = t.get("raw", "")
        if lang:
            return f"\\begin{{lstlisting}}[language={lang}]\n{code}\\end{{lstlisting}}"
        return f"\\begin{{verbatim}}\n{code}\\end{{verbatim}}"

    if type_ == "thematic_break":
        return "\\hrule"

    if type_ == "table":
        return _render_table(t, image_map, fn_map)

    return ""


def _render_table(t, image_map, fn_map):
    children = t.get("children", [])

    aligns = []
    for part in children:
        if part.get("type") == "table_head":
            for cell in part.get("children", []):
                a = cell.get("attrs", {}).get("align")
                aligns.append(
                    "l" if a is None or a == "left"
                    else "c" if a == "center"
                    else "r"
                )
            break

    spec = "".join(aligns) if aligns else "l"
    lines = [f"\\begin{{tabular}}{{{spec}}}"]
    lines.append("\\toprule")

    for part in children:
        if part.get("type") == "table_head":
            cells = part.get("children", [])
            row_cells = []
            for cell in cells:
                cell_text = render_inline_compact(
                    cell.get("children", []), image_map, fn_map
                )
                row_cells.append(f"\\textbf{{{cell_text}}}")
            lines.append(" & ".join(row_cells) + " \\\\")
            lines.append("\\midrule")

        elif part.get("type") == "table_body":
            for row in part.get("children", []):
                if row.get("type") == "table_row":
                    cells = row.get("children", [])
                    row_cells = []
                    for cell in cells:
                        cell_text = render_inline_compact(
                            cell.get("children", []), image_map, fn_map
                        )
                        row_cells.append(cell_text)
                    lines.append(" & ".join(row_cells) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    return "\n".join(lines)
