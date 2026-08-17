"""Best-effort browser auto-fill for Greenhouse and Lever application forms.

Reaper opens the posting in a real Chromium window, matches the answer-pack
fields onto the form's labelled inputs, uploads the resume PDF where possible,
and then STOPS. It never submits. The user reviews and clicks submit.

Any unrecognised ATS falls back to the paste sheet; this module just reports
that it could not drive the form.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AutofillResult:
    attempted: bool
    platform: str | None
    filled: list[str]
    message: str


def detect_platform(url: str) -> str | None:
    low = url.lower()
    if "greenhouse.io" in low or "grnh.se" in low:
        return "greenhouse"
    if "lever.co" in low:
        return "lever"
    return None


def _fill_by_label(page, field_map: dict[str, str]) -> list[str]:
    """Match each visible text input/textarea to an answer-pack key by its label text."""
    filled: list[str] = []
    inputs = page.query_selector_all(
        "input[type='text'], input[type='email'], input[type='tel'], "
        "input:not([type]), textarea"
    )
    for el in inputs:
        try:
            if not el.is_visible():
                continue
            label = _label_for(page, el).lower()
            if not label:
                continue
            value = _match_value(label, field_map)
            if value and not el.input_value():
                el.fill(value)
                filled.append(label.strip()[:60])
        except Exception:  # noqa: BLE001 - skip any element that misbehaves
            continue
    return filled


def _label_for(page, el) -> str:
    # aria-label / placeholder / associated <label> / nearby label text.
    for attr in ("aria-label", "placeholder", "name"):
        val = el.get_attribute(attr)
        if val:
            return val
    el_id = el.get_attribute("id")
    if el_id:
        lab = page.query_selector(f"label[for='{el_id}']")
        if lab:
            return lab.inner_text()
    return ""


def _match_value(label: str, field_map: dict[str, str]) -> str | None:
    # Longer keys first so "first name" wins over "name".
    for key in sorted(field_map, key=len, reverse=True):
        if key in label:
            return field_map[key]
    if "authoriz" in label or "eligible to work" in label:
        return field_map.get("authorized")
    if "sponsor" in label:
        return field_map.get("sponsorship")
    return None


def _upload_resume(page, resume_pdf: Path) -> bool:
    for sel in ("input[type='file']",):
        el = page.query_selector(sel)
        if el:
            try:
                el.set_input_files(str(resume_pdf))
                return True
            except Exception:  # noqa: BLE001
                pass
    return False


def autofill(
    url: str, field_map: dict[str, str], resume_pdf: Path | None
) -> AutofillResult:
    platform = detect_platform(url)
    if not platform:
        return AutofillResult(
            attempted=False,
            platform=None,
            filled=[],
            message="Unrecognised ATS. Use the answer-pack paste sheet instead.",
        )

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return AutofillResult(
            False, platform, [],
            "Playwright is not installed. Run: pip install playwright && playwright install chromium",
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(1500)
            filled = _fill_by_label(page, field_map)
            uploaded = False
            if resume_pdf and resume_pdf.exists():
                uploaded = _upload_resume(page, resume_pdf)
            msg = (
                f"Filled {len(filled)} field(s) on the {platform} form"
                + (", uploaded resume PDF" if uploaded else "")
                + ". Review everything, then submit manually. Reaper never submits."
            )
            input("\nBrowser is open and pre-filled. Press Enter here to close it "
                  "(submit in the browser first if it looks right)... ")
            return AutofillResult(True, platform, filled, msg)
        finally:
            browser.close()
