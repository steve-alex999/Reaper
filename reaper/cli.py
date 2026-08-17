"""Reaper CLI.

    reaper apply <URL> [--jd-file FILE] [--no-autofill] [--yes] [--model M]
    reaper prescreen <URL>

`apply` runs the full pipeline: fetch -> pre-screen -> three-prompt workflow ->
compile resume -> answer pack -> optional browser auto-fill. Everything lands in
applications/<company>-<role>-<date>/.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

from reaper import __version__
from reaper.answer_pack import build_answer_pack
from reaper.autofill import autofill, detect_platform
from reaper.jd_fetch import fetch_jd, load_jd_from_file
from reaper.prescreen import prescreen
from reaper.resume import compile_resume

APPLICATIONS_DIR = Path("applications")


def _slug(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text or "").strip("-").lower()
    return text[:50] or "role"


def _print_header(title: str) -> None:
    print(f"\n{'=' * 64}\n{title}\n{'=' * 64}")


def _confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    try:
        return input(f"{prompt} [y/N] ").strip().lower() in ("y", "yes")
    except EOFError:
        return False


def _render_analysis(a: dict) -> str:
    kw = "\n".join(
        f"    [{'x' if k['present_in_profile'] else ' '}] {k['keyword']}"
        for k in a.get("top_keywords", [])
    )
    flags = "\n".join(f"    - {f}" for f in a.get("red_flags", []))
    return (
        f"  Company : {a.get('company')}\n"
        f"  Role    : {a.get('role_title')}\n"
        f"  Score   : {a.get('match_score')}/100  ({a.get('fit_band')})\n"
        f"  Base    : {a.get('resume_base')} resume\n"
        f"  Verdict : {a.get('verdict', '').upper()} - {a.get('verdict_reason')}\n"
        f"  Top ATS keywords (x = supported by profile):\n{kw}\n"
        f"  Red flags:\n{flags}"
    )


def cmd_prescreen(args: argparse.Namespace) -> int:
    posting = _load_posting(args)
    _print_header("Pre-screen")
    print(prescreen(posting.text).summary())
    return 0


def cmd_prompts(args: argparse.Namespace) -> int:
    """API-free: emit the ready-to-paste prompt bundle for a manual chat run."""
    posting = _load_posting(args)
    _print_header(f"Fetched JD ({posting.method}, {len(posting.text)} chars)")
    ps = prescreen(posting.text)
    print(ps.summary())

    # Imported here so this command never needs the anthropic package installed.
    from reaper.workflow import build_prompt_bundle
    from reaper.answer_pack import build_answer_pack

    out_dir = APPLICATIONS_DIR / f"manual-{_dt.date.today().isoformat()}"
    bundle_dir = out_dir / "prompts"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "jd.txt").write_text(posting.text, encoding="utf-8")
    (out_dir / "prescreen.txt").write_text(ps.summary(), encoding="utf-8")
    for name, content in build_prompt_bundle(posting.text, ps).items():
        (bundle_dir / name).write_text(content, encoding="utf-8")

    # The identity half of the answer pack is static; drop it now so only the
    # tailored screener answers need to come back from the chat.
    pack = build_answer_pack("(fill company)", "(fill role)", {})
    (out_dir / "answer_pack.md").write_text(
        pack.to_markdown("resume.pdf"), encoding="utf-8"
    )

    _print_header("Manual prompt bundle written")
    print(f"  {bundle_dir}/  (paste 00 then 01-04 into claude.ai, in order)")
    print(f"  {out_dir / 'answer_pack.md'}  (static identity fields)")
    print("\nThen: save the step-03 LaTeX to resume.tex and run "
          "`reaper compile resume.tex`.")
    return 0


def cmd_compile(args: argparse.Namespace) -> int:
    """Compile a .tex the user got back from a manual run into a PDF."""
    tex_path = Path(args.tex_file)
    if not tex_path.exists():
        print(f"No such file: {tex_path}", file=sys.stderr)
        return 2
    comp = compile_resume(
        tex_path.read_text(encoding="utf-8"),
        tex_path.parent,
        stem=tex_path.stem,
    )
    print(comp.message)
    if comp.pdf_path:
        print(f"PDF: {comp.pdf_path}")
        return 0
    return 1


def cmd_apply(args: argparse.Namespace) -> int:
    posting = _load_posting(args)
    _print_header(f"Fetched JD ({posting.method}, {len(posting.text)} chars)")

    ps = prescreen(posting.text)
    print(ps.summary())
    if ps.should_skip and not args.yes:
        if not _confirm("\nPre-screen found a hard blocker. Continue anyway?", args.yes):
            print("Stopped. This role looks like a skip.")
            return 0

    # Lazy import so `reaper prescreen` never needs the anthropic package.
    from reaper.workflow import run_workflow

    _print_header("Running three-prompt workflow (this takes a minute)")
    try:
        result = run_workflow(posting.text, ps, model=args.model)
    except Exception as exc:  # noqa: BLE001 - surface a clean message to the user
        msg = str(exc)
        if "auth" in msg.lower() or "api_key" in msg.lower() or "x-api-key" in msg.lower():
            print(
                "No Claude credentials found. Set ANTHROPIC_API_KEY (export "
                "ANTHROPIC_API_KEY=sk-ant-...) or run `ant auth login`, then retry.",
                file=sys.stderr,
            )
        else:
            print(f"Workflow failed: {exc}", file=sys.stderr)
        return 1

    a = result.analysis
    _print_header("Recruiter analysis")
    print(_render_analysis(a))

    out_dir = APPLICATIONS_DIR / (
        f"{_slug(a.get('company', 'company'))}-{_slug(a.get('role_title', 'role'))}"
        f"-{_dt.date.today().isoformat()}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "jd.txt").write_text(posting.text, encoding="utf-8")
    (out_dir / "analysis.json").write_text(json.dumps(a, indent=2), encoding="utf-8")
    (out_dir / "prescreen.txt").write_text(ps.summary(), encoding="utf-8")
    (out_dir / "experience_rewrite.md").write_text(
        result.experience_rewrite, encoding="utf-8"
    )
    (out_dir / "ats_notes.md").write_text(result.ats_notes, encoding="utf-8")

    _print_header("Compiling resume")
    comp = compile_resume(result.resume_tex, out_dir)
    print(comp.message)

    pack = build_answer_pack(
        a.get("company", ""), a.get("role_title", ""), result.screener
    )
    pdf_name = comp.pdf_path.name if comp.pdf_path else None
    (out_dir / "answer_pack.md").write_text(
        pack.to_markdown(pdf_name), encoding="utf-8"
    )

    _print_header("Artifacts")
    for f in sorted(out_dir.iterdir()):
        print(f"  {f}")

    # Auto-fill decision.
    if args.no_autofill or posting.url.startswith("file://"):
        print("\nAuto-fill skipped. Use answer_pack.md to fill the form.")
        return 0

    platform = detect_platform(posting.url)
    if not platform:
        print(
            "\nATS not recognised for auto-fill (supported: Greenhouse, Lever). "
            "Use answer_pack.md to paste your answers."
        )
        return 0

    if a.get("verdict") == "skip" and not args.yes:
        if not _confirm(
            f"\nVerdict is SKIP. Still open the {platform} form to auto-fill?", args.yes
        ):
            return 0

    if not _confirm(
        f"\nOpen the {platform} form in a browser and auto-fill it now?", args.yes
    ):
        print("Auto-fill skipped. answer_pack.md has everything to paste.")
        return 0

    _print_header(f"Auto-filling {platform} form")
    res = autofill(posting.url, pack.field_map(), comp.pdf_path)
    print(res.message)
    return 0


def _load_posting(args: argparse.Namespace):
    if getattr(args, "jd_file", None):
        return load_jd_from_file(args.jd_file)
    return fetch_jd(args.url)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="reaper", description="Reap a job posting into a tailored application."
    )
    p.add_argument("--version", action="version", version=f"reaper {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    ap = sub.add_parser("apply", help="run the full pipeline on a job link")
    ap.add_argument("url", nargs="?", help="the job-application URL")
    ap.add_argument("--jd-file", help="read the JD from a local file instead of a URL")
    ap.add_argument("--no-autofill", action="store_true", help="never open a browser")
    ap.add_argument("--yes", action="store_true", help="assume yes to all prompts")
    ap.add_argument("--model", help="override the Claude model")
    ap.set_defaults(func=cmd_apply)

    sp = sub.add_parser("prescreen", help="run only the deterministic pre-screen")
    sp.add_argument("url", nargs="?", help="the job-application URL")
    sp.add_argument("--jd-file", help="read the JD from a local file instead of a URL")
    sp.set_defaults(func=cmd_prescreen)

    pr = sub.add_parser(
        "prompts",
        help="API-free: emit a paste-into-claude.ai prompt bundle (no API call)",
    )
    pr.add_argument("url", nargs="?", help="the job-application URL")
    pr.add_argument("--jd-file", help="read the JD from a local file instead of a URL")
    pr.set_defaults(func=cmd_prompts)

    cp = sub.add_parser("compile", help="compile a .tex resume to PDF")
    cp.add_argument("tex_file", help="path to the .tex file")
    cp.set_defaults(func=cmd_compile)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Commands that take a job posting must be given a URL or a --jd-file.
    if hasattr(args, "url") and not args.url and not getattr(args, "jd_file", None):
        print("Provide a URL or --jd-file.", file=sys.stderr)
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
