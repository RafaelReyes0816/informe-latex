import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .converter import parse, _render_block
from .deps import compile_pdf, ensure_compile_available, status_report
from .image_handler import handle_images
from .template import list_templates, load_template, apply_template
from .project import ProjectConfig

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")


class FileListFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.paths: list[Path] = []
        self.labels: list[ctk.CTkLabel] = []

    def add_file(self, path: Path) -> None:
        if path in self.paths:
            return
        self.paths.append(path)
        row = len(self.labels)
        lbl = ctk.CTkLabel(self, text=path.name, anchor="w")
        lbl.grid(row=row, column=0, sticky="ew", pady=1)
        self.labels.append(lbl)
        self._parent_canvas.yview_moveto(1.0)

    def remove_selected(self, index: int) -> None:
        if 0 <= index < len(self.paths):
            del self.paths[index]
            self.labels[index].destroy()
            del self.labels[index]
            self._reflow()

    def _reflow(self) -> None:
        for i, lbl in enumerate(self.labels):
            lbl.grid_configure(row=i)

    def clear(self) -> None:
        for lbl in self.labels:
            lbl.destroy()
        self.labels.clear()
        self.paths.clear()

    def get_stems(self) -> list[str]:
        return [p.stem for p in self.paths]


class ConfigPanel(ctk.CTkFrame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app

        row = 0

        ctk.CTkLabel(self, text="Título:", anchor="w").grid(
            row=row, column=0, sticky="ew", pady=(0, 2)
        )
        row += 1
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        row += 1

        ctk.CTkLabel(self, text="Autor:", anchor="w").grid(
            row=row, column=0, sticky="ew", pady=(0, 2)
        )
        row += 1
        self.author_entry = ctk.CTkEntry(self)
        self.author_entry.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        row += 1

        ctk.CTkLabel(self, text="Template:", anchor="w").grid(
            row=row, column=0, sticky="ew", pady=(0, 2)
        )
        row += 1
        self.template_var = ctk.StringVar(value="default")
        self.template_menu = ctk.CTkOptionMenu(
            self, variable=self.template_var, values=list_templates()
        )
        self.template_menu.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        row += 1

        ctk.CTkLabel(self, text="Archivos .md:", anchor="w").grid(
            row=row, column=0, sticky="ew", pady=(0, 2)
        )
        row += 1
        self.file_list = FileListFrame(self, height=120)
        self.file_list.grid(row=row, column=0, sticky="ew", pady=(0, 4))
        row += 1

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame, text="+ Añadir", command=self._add_file
        ).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        ctk.CTkButton(
            btn_frame, text="✕ Quitar", command=self._remove_file
        ).grid(row=0, column=1, padx=(4, 0), sticky="ew")
        row += 1

        ctk.CTkLabel(self, text="Directorio salida:", anchor="w").grid(
            row=row, column=0, sticky="ew", pady=(0, 2)
        )
        row += 1
        out_frame = ctk.CTkFrame(self, fg_color="transparent")
        out_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        out_frame.grid_columnconfigure(0, weight=1)

        self.out_dir_var = ctk.StringVar(value=".")
        ctk.CTkEntry(
            out_frame, textvariable=self.out_dir_var
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(
            out_frame, text="📁", width=36, command=self._browse_dir
        ).grid(row=0, column=1)
        row += 1

        self.copy_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self, text="Copiar imágenes a figures/", variable=self.copy_var
        ).grid(row=row, column=0, sticky="w", pady=2)
        row += 1

        self.compile_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self, text="Compilar con latexmk", variable=self.compile_var
        ).grid(row=row, column=0, sticky="w", pady=2)
        row += 1

        self.open_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self, text="Abrir PDF al finalizar", variable=self.open_var
        ).grid(row=row, column=0, sticky="w", pady=2)
        row += 1

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=row, column=0, sticky="ew", pady=(10, 0))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_row, text="💾 Guardar proyecto",
            command=self._save_project, fg_color="gray"
        ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.generate_btn = ctk.CTkButton(
            btn_row, text="▶ Generar Informe",
            command=self._generate
        )
        self.generate_btn.grid(row=0, column=1, padx=(4, 0), sticky="ew")

        self.grid_columnconfigure(0, weight=1)

    def _add_file(self) -> None:
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos Markdown",
            filetypes=[("Markdown", "*.md"), ("Todos", "*.*")],
        )
        for f in files:
            self.file_list.add_file(Path(f))
        self._preview_first_file()

    def _remove_file(self) -> None:
        if not self.file_list.paths:
            return
        self.file_list.remove_selected(len(self.file_list.paths) - 1)

    def _browse_dir(self) -> None:
        d = filedialog.askdirectory(title="Directorio de salida")
        if d:
            self.out_dir_var.set(d)

    def _save_project(self) -> None:
        cfg = self._collect_config()
        cfg.save()
        self.app.status.configure(text="💾 Proyecto guardado")

    def _collect_config(self) -> ProjectConfig:
        return ProjectConfig(
            files=[str(p) for p in self.file_list.paths],
            title=self.title_entry.get(),
            author=self.author_entry.get(),
            template=self.template_var.get(),
            output_dir=self.out_dir_var.get(),
            copy_images=self.copy_var.get(),
            compile_pdf=self.compile_var.get(),
            open_pdf=self.open_var.get(),
        )

    def restore_config(self, cfg: ProjectConfig) -> None:
        self.title_entry.insert(0, cfg.title)
        self.author_entry.insert(0, cfg.author)
        self.template_var.set(cfg.template or "default")
        self.out_dir_var.set(cfg.output_dir or ".")
        self.copy_var.set(cfg.copy_images)
        self.compile_var.set(cfg.compile_pdf)
        self.open_var.set(cfg.open_pdf)
        for f in cfg.files:
            p = Path(f)
            if p.is_file():
                self.file_list.add_file(p)

    def _preview_first_file(self) -> None:
        if self.file_list.paths:
            path = self.file_list.paths[0]
            self.app.preview_panel.show_markdown(path)

    def _generate(self) -> None:
        cfg = self._collect_config()

        if not cfg.files:
            messagebox.showwarning("Sin archivos", "Añade al menos un archivo .md")
            return
        if not cfg.title:
            cfg.title = Path(cfg.files[0]).stem

        self.generate_btn.configure(state="disabled", text="⏳ Trabajando...")
        self.app.status.configure(text="⏳ Generando...")
        self.app.preview_panel.clear_log()

        t = threading.Thread(target=self._generate_worker, args=(cfg,), daemon=True)
        t.start()

    def _generate_worker(self, cfg: ProjectConfig) -> None:
        try:
            out_dir = Path(cfg.output_dir or ".").resolve()
            out_dir.mkdir(parents=True, exist_ok=True)

            date_str = datetime.now().strftime("%Y-%m-%d")
            all_content = []
            file_stems = []

            for file_path_str in cfg.files:
                md_path = Path(file_path_str)
                if not md_path.is_file():
                    self._log(f"⚠ Saltando: {md_path.name} (no encontrado)")
                    continue

                md_text = md_path.read_text(encoding="utf-8")
                tokens, fn_map = parse(md_text)

                image_map = {}
                if cfg.copy_images:
                    image_map = handle_images(tokens, out_dir)

                content = _render_block(tokens, image_map, fn_map)
                all_content.append(content)
                file_stems.append(md_path.stem)

                if image_map:
                    self._log(f"📷 {md_path.name}: {len(image_map)} imagen(es) copiadas")

                self._preview_latex(content)

            if len(file_stems) > 1:
                from .template import build_latex_multi
                latex = build_latex_multi(
                    cfg.title, cfg.author, date_str, file_stems, cfg.template
                )
                for stem, content in zip(file_stems, all_content):
                    part_path = out_dir / f"{stem}.tex"
                    template = load_template(cfg.template)
                    part = apply_template(
                        template, cfg.title, cfg.author, date_str, content
                    )
                    part_path.write_text(part, encoding="utf-8")
                    self._log(f"📄 {part_path.name} guardado")
                out_name = f"{cfg.title}.tex"
            else:
                single_content = all_content[0] if all_content else ""
                template = load_template(cfg.template)
                latex = apply_template(
                    template, cfg.title, cfg.author, date_str, single_content
                )
                out_name = f"{file_stems[0]}.tex" if file_stems else "output.tex"

            out_path = out_dir / out_name
            out_path.write_text(latex, encoding="utf-8")
            self._log(f"✅ {out_path.name} generado ({len(latex)} chars)")

            if cfg.compile_pdf:
                self._compile(out_path)

            if cfg.open_pdf:
                pdf_path = out_path.with_suffix(".pdf")
                if pdf_path.is_file():
                    cmd = (
                        ["xdg-open", str(pdf_path)] if sys.platform == "linux"
                        else ["open", str(pdf_path)] if sys.platform == "darwin"
                        else ["start", str(pdf_path)]
                    )
                    subprocess.Popen(cmd)

            self._on_finish(True, f"✅ Informe generado: {out_path.name}")

        except Exception as e:
            self._log(f"❌ Error: {e}")
            self._on_finish(False, f"❌ Error: {e}")

    def _compile(self, tex_path: Path) -> None:
        env_msg = ensure_compile_available()
        if env_msg:
            self._log("⚠ No se puede compilar el PDF: faltan dependencias.")
            self._log(env_msg)
            return

        self._log("Estado del entorno:")
        self._log(status_report())

        ok, cmsg = compile_pdf(tex_path)
        self._log(cmsg)

    def _log(self, msg: str) -> None:
        self.app.after(0, self.app.preview_panel.append_log, msg)

    def _preview_latex(self, content: str) -> None:
        self.app.after(0, lambda: self.app.preview_panel.replace_latex(content))

    def _on_finish(self, success: bool, msg: str) -> None:
        def _done():
            self.generate_btn.configure(state="normal", text="▶ Generar Informe")
            self.app.status.configure(text=msg)
        self.app.after(0, _done)


class PreviewPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.md_tab = self.tabview.add("Markdown")
        self.latex_tab = self.tabview.add("LaTeX")
        self.log_tab = self.tabview.add("Log")

        for tab, lang in [
            (self.md_tab, "markdown"),
            (self.latex_tab, "latex"),
            (self.log_tab, "log"),
        ]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)

        self.md_text = ctk.CTkTextbox(self.md_tab, wrap="word", state="disabled")
        self.md_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.latex_text = ctk.CTkTextbox(self.latex_tab, wrap="word", state="disabled")
        self.latex_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.log_text = ctk.CTkTextbox(self.log_tab, wrap="word", state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def show_markdown(self, path: Path) -> None:
        try:
            text = path.read_text(encoding="utf-8")
            self.md_text.configure(state="normal")
            self.md_text.delete("1.0", "end")
            self.md_text.insert("1.0", text)
            self.md_text.configure(state="disabled")
        except Exception as e:
            self.md_text.configure(state="normal")
            self.md_text.delete("1.0", "end")
            self.md_text.insert("1.0", f"Error al leer: {e}")
            self.md_text.configure(state="disabled")

    def replace_latex(self, content: str) -> None:
        self.latex_text.configure(state="normal")
        self.latex_text.delete("1.0", "end")
        self.latex_text.insert("1.0", content)
        self.latex_text.configure(state="disabled")
        self.tabview.set("LaTeX")

    def append_log(self, msg: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def clear_log(self) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("md2tex — Conversor Markdown a LaTeX")
        self.geometry("1050x720")
        self.minsize(800, 500)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main = ctk.CTkFrame(self)
        main.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        main.grid_columnconfigure(0, weight=0, minsize=340)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        self.config_panel = ConfigPanel(main, self)
        self.config_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.preview_panel = PreviewPanel(main)
        self.preview_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.status = ctk.CTkLabel(
            self, text="Listo", anchor="w", height=28
        )
        self.status.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        cfg = ProjectConfig.load()
        self.config_panel.restore_config(cfg)
        if cfg.files:
            self.config_panel._preview_first_file()

    def _on_close(self) -> None:
        cfg = self.config_panel._collect_config()
        cfg.save()
        self.destroy()


def main():
    app = App()
    app.mainloop()
