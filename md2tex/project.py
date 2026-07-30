import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional


@dataclass
class ProjectConfig:
    files: list = field(default_factory=list)
    title: str = ""
    author: str = ""
    template: str = "default"
    output_dir: str = "."
    copy_images: bool = True
    compile_pdf: bool = True
    open_pdf: bool = False

    SAVE_FILE = ".md2tex_project.json"

    def save(self, path: Optional[str] = None) -> None:
        base = Path(path or self.output_dir or ".").resolve()
        data = asdict(self)
        data["files"] = [str(f) for f in data["files"]]
        (base / self.SAVE_FILE).write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @classmethod
    def load(cls, path: Optional[str] = None) -> "ProjectConfig":
        candidates = [
            Path(path).resolve() / cls.SAVE_FILE if path else None,
            Path(cls.SAVE_FILE),
            Path.home() / cls.SAVE_FILE,
        ]
        for f in candidates:
            if f and f.is_file():
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    return cls(**data)
                except (json.JSONDecodeError, TypeError):
                    continue
        return cls()
