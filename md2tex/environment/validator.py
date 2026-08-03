from __future__ import annotations

from pathlib import Path

from .base import EnvironmentBase, EnvironmentInfo
from .checker import EnvironmentChecker


class EnvironmentValidator:
    REQUIRED_TOOLS = ("latexmk", "perl", "pdflatex", "kpsewhich")
    REQUIRED_PACKAGES = [
        "amsmath", "amssymb", "graphicx", "hyperref", "booktabs",
        "array", "xcolor", "listings", "geometry", "setspace", "babel",
    ]

    @classmethod
    def validate(cls) -> dict:
        tools = EnvironmentChecker.latex_dependencies()
        packages = EnvironmentChecker.packages_available()
        compilers = EnvironmentChecker.available_compilers()
        disk_ok, disk_msg = EnvironmentChecker.check_disk_space()
        permissions = EnvironmentChecker.check_permissions()

        missing_tools = [t for t in cls.REQUIRED_TOOLS if not tools.get(t)]
        missing_packages = (
            [p for p in cls.REQUIRED_PACKAGES if not packages.get(p)]
            if packages else []
        )

        backend, detail = EnvironmentChecker.preferred_backend()
        compile_ok = backend is not None

        if compile_ok:
            compile_result, _ = cls._test_compilation(backend)
            compile_ok = compile_result

        all_ok = (
            not missing_tools
            and not missing_packages
            and compile_ok
            and disk_ok
            and all(permissions.values())
        )

        return {
            "system": EnvironmentChecker.detect_os(),
            "tools": tools,
            "packages": packages,
            "compilers": compilers,
            "disk_space": (disk_ok, disk_msg),
            "permissions": permissions,
            "missing_tools": missing_tools,
            "missing_packages": missing_packages,
            "backend": backend,
            "backend_detail": detail,
            "compile_ok": compile_ok,
            "all_ok": all_ok,
        }

    @classmethod
    def validate_template(cls, template_name: str = "default") -> bool:
        try:
            from md2tex.template import list_templates, load_template, TEMPLATES_DIR
            templates = list_templates()
            if template_name not in templates and template_name != "default":
                return False
            template_content = load_template(template_name)
            if not template_content or "{CONTENT}" not in template_content:
                return False
            return True
        except Exception:
            return False

    @classmethod
    def validate_resources(cls) -> dict:
        results = {}
        try:
            from md2tex.template import TEMPLATES_DIR
            results["templates_dir"] = str(TEMPLATES_DIR)
            results["templates_dir_exists"] = TEMPLATES_DIR.is_dir()
            results["templates_available"] = (
                [f.stem for f in TEMPLATES_DIR.glob("*.tex")]
                if TEMPLATES_DIR.is_dir() else []
            )
        except Exception as e:
            results["templates_dir"] = None
            results["templates_dir_exists"] = False
            results["templates_available"] = []
            results["error"] = str(e)

        results["default_template_valid"] = cls.validate_template("default")
        return results

    @staticmethod
    def _test_compilation(backend: str) -> tuple[bool, str]:
        from .compiler import LatexCompiler
        return LatexCompiler.diagnose_compile()
