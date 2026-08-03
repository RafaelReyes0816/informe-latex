from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Motores por defecto (orden de preferencia, modo automático).
COMPILER_ORDER = ("xelatex", "lualatex", "pdflatex")


def _run_silent(cmd: list) -> None:
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass


def _needs_miktex_update_check(text: str) -> bool:
    t = (text or "").lower()
    return (
        "not checked for miktex updates" in t
        or "no se ha comprobado" in t
        or "major issue: so far" in t
    )


def _pass_record(cmd: list, res: "subprocess.CompletedProcess") -> str:
    out = (res.stdout or "")
    err = (res.stderr or "")
    return (
        f"$ {' '.join(cmd)}\n[exit {res.returncode}]\n"
        f"--- stdout ---\n{out}\n--- stderr ---\n{err}"
    )


def _write_log(
    path: Path, cmd: list, output: str, err: str,
    exit_code, reason: str, backend: str, detail: str,
) -> None:
    header = [
        f"md2tex compile log — {datetime.now().isoformat(timespec='seconds')}",
        f"backend: {backend} ({detail})",
        f"cmd: {' '.join(cmd)}",
        f"cwd: {path.parent}",
        f"exit code: {exit_code}",
        f"reason: {reason or 'n/a'}", "",
    ]
    path.write_text("\n".join(header) + output + "\n", encoding="utf-8")


def _append_log(path: Path, res: "subprocess.CompletedProcess") -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write("\n--- retry ---\n")
        f.write(_pass_record(["<retry>"], res))


_MISKTIP_HINT = (
    "\n\nSi MiKTeX no tiene actualizada la base de datos de paquetes, "
    "ejecute `mpm --update-db` o abra MiKTeX Console → tareas → "
    "actualizar base de datos de paquetes."
)

_HUMAN_NAMES = {
    "latexmk": "latexmk",
    "xelatex": "XeLaTeX",
    "lualatex": "LuaLaTeX",
    "pdflatex": "pdfLaTeX",
}


class LatexCompiler:
    def __init__(self, tex_path, cwd=None, log_dir=None, engine="auto"):
        self.tex_path = Path(tex_path)
        self.cwd = Path(cwd) if cwd else self.tex_path.parent
        self.log_dir = Path(log_dir) if log_dir else self.cwd
        self.engine = engine or "auto"

    def _pick(self) -> tuple:
        from .checker import EnvironmentChecker
        return EnvironmentChecker.resolve_backend(self.engine)

    def _build_command(self, backend: str) -> list:
        if backend == "latexmk":
            return ["latexmk", "-pdf", self.tex_path.name]
        return [
            backend, "-interaction=nonstopmode",
            "-halt-on-error", self.tex_path.name,
        ]

    def compile(self) -> tuple:
        backend, detail = self._pick()
        if backend is None:
            from .checker import EnvironmentChecker
            if self.engine and str(self.engine).strip().lower() not in ("auto", ""):
                return False, f"⚠ No se pudo compilar: {detail}"
            return False, EnvironmentChecker.ensure_compile_available()

        if sys.platform == "win32":
            _run_silent(["initexmf", "--update-fndb"])
            _run_silent(["initexmf", "--set-config-value=[MPM]AutoInstall=1"])

        cmd = self._build_command(backend)
        # latexmk resuelve pasadas por sí solo; el resto requiere 2 pasadas.
        passes = 1 if backend == "latexmk" else 2

        log_path = self.log_dir / f"md2tex-compile-{self.tex_path.stem}.log"
        chunks = []
        res = None
        for _ in range(passes):
            try:
                res = subprocess.run(
                    cmd, cwd=str(self.cwd), stdin=subprocess.DEVNULL,
                    capture_output=True, text=True, timeout=300,
                )
            except subprocess.TimeoutExpired:
                _write_log(
                    log_path, cmd, "", "", None,
                    "TIMEOUT (>300s)", backend, detail,
                )
                return False, (
                    f"⚠ Compilación excedió el tiempo máximo (300 s)."
                    f"\nVer log: {log_path}"
                )
            except FileNotFoundError:
                return False, f"⚠ {_HUMAN_NAMES.get(backend, backend)} no está disponible en el PATH."

            chunks.append(_pass_record(cmd, res))
            if res.returncode != 0:
                break

        _write_log(
            log_path, cmd, "\n---\n".join(chunks),
            "", res.returncode, "", backend, detail,
        )

        if res.returncode == 0:
            return True, (
                f"📄 {self.tex_path.stem}.pdf compilado ({detail})"
                f"\nLog: {log_path}"
            )

        tail = (res.stderr or res.stdout or "").strip()
        hint = ""
        if (
            sys.platform == "win32"
            and _needs_miktex_update_check(tail)
        ):
            _run_silent(["mpm", "--update-db"])
            retry = subprocess.run(
                cmd, cwd=str(self.cwd), stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=300,
            )
            if retry.returncode == 0:
                _append_log(log_path, retry)
                return True, (
                    f"📄 {self.tex_path.stem}.pdf compilado ({detail}; "
                    f"reconstruida DB de MiKTeX)\nLog: {log_path}"
                )
            tail = (retry.stderr or retry.stdout or "").strip()[-800:]
        elif backend in COMPILER_ORDER:
            hint = _MISKTIP_HINT

        return False, (
            f"⚠ Compilación fallida ({detail}).\n{tail[-800:]}{hint}\nLog: {log_path}"
        )

    @classmethod
    def diagnose_compile(cls, engine="auto") -> tuple:
        from .checker import EnvironmentChecker
        backend, detail = EnvironmentChecker.resolve_backend(engine)
        if backend is None:
            return False, detail

        workdir = Path(tempfile.mkdtemp(prefix="md2tex-diag-"))
        tex = workdir / "test.tex"
        tex.write_text(
            "\\documentclass{article}\\begin{document}"
            "Instalación correcta\\end{document}\n",
            encoding="utf-8",
        )
        try:
            if backend == "latexmk":
                cmd = ["latexmk", "-pdf", tex.name]
            else:
                cmd = [
                    backend, "-interaction=nonstopmode",
                    "-halt-on-error", tex.name,
                ]
            res = subprocess.run(
                cmd, cwd=str(workdir), stdin=subprocess.DEVNULL,
                capture_output=True, text=True, timeout=180,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, "error al compilar (motor no disponible)"
        pdf = workdir / "test.pdf"
        ok = res.returncode == 0 and pdf.is_file()
        return ok, (
            "OK (test.pdf generado)" if ok
            else f"falló (exit {res.returncode})"
        )


def compile_pdf(tex_path, cwd=None, log_dir=None, engine="auto") -> tuple:
    return LatexCompiler(tex_path, cwd, log_dir, engine).compile()
