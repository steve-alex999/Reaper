"""Write the tailored .tex and compile it to PDF when an engine is available.

Tries tectonic first (self-contained), then latexmk/pdflatex. If none is
installed, leaves the .tex and tells the user how to compile it (Overleaf or a
local install).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompileResult:
    tex_path: Path
    pdf_path: Path | None
    engine: str | None
    message: str


def _run(cmd: list[str], cwd: Path) -> bool:
    try:
        proc = subprocess.run(  # noqa: S603 - fixed engine binaries, controlled args
            cmd, cwd=cwd, capture_output=True, text=True, timeout=180
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def compile_resume(tex_source: str, out_dir: Path, stem: str = "resume") -> CompileResult:
    out_dir.mkdir(parents=True, exist_ok=True)
    tex_path = out_dir / f"{stem}.tex"
    tex_path.write_text(tex_source, encoding="utf-8")
    pdf_path = out_dir / f"{stem}.pdf"

    if not tex_source.strip():
        return CompileResult(tex_path, None, None, "No LaTeX was produced.")

    if shutil.which("tectonic"):
        if _run(["tectonic", tex_path.name], out_dir) and pdf_path.exists():
            return CompileResult(tex_path, pdf_path, "tectonic", "Compiled with tectonic.")

    if shutil.which("latexmk"):
        if _run(["latexmk", "-pdf", "-interaction=nonstopmode", tex_path.name], out_dir) \
                and pdf_path.exists():
            return CompileResult(tex_path, pdf_path, "latexmk", "Compiled with latexmk.")

    if shutil.which("pdflatex"):
        ok = _run(["pdflatex", "-interaction=nonstopmode", tex_path.name], out_dir)
        # Note: the `resume.cls` document class must be on TEXMF for this to work.
        if ok and pdf_path.exists():
            return CompileResult(tex_path, pdf_path, "pdflatex", "Compiled with pdflatex.")

    return CompileResult(
        tex_path,
        None,
        None,
        "No LaTeX engine found (tried tectonic, latexmk, pdflatex). "
        "The .tex is saved. Compile it on Overleaf or install a TeX engine. "
        "Note: this template needs the `resume` document class.",
    )
