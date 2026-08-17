"""Fetch a job description from a pasted URL.

Strategy: try a plain HTTP GET and strip the HTML to text. If the page looks
like a JavaScript shell (too little text, or a known JS-heavy ATS), fall back to
Playwright, which is pre-installed in this environment.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.request import Request, urlopen

# ATS hosts whose posting pages are rendered client-side; go straight to a browser.
JS_HEAVY_HOSTS = (
    "myworkdayjobs.com",
    "workday",
    "icims.com",
    "linkedin.com",
    "ashbyhq.com",
    "smartrecruiters.com",
    "eightfold.ai",
)

_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


@dataclass
class JobPosting:
    url: str
    text: str
    method: str  # "http" or "browser"

    @property
    def is_thin(self) -> bool:
        return len(self.text) < 600


class _TextExtractor(HTMLParser):
    """Collect visible text, dropping script/style and collapsing whitespace."""

    _SKIP = {"script", "style", "noscript", "head", "svg"}

    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skipping = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self._SKIP:
            self._skipping += 1
        if tag in ("p", "br", "li", "div", "h1", "h2", "h3", "h4", "tr"):
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP and self._skipping:
            self._skipping -= 1

    def handle_data(self, data: str) -> None:
        if not self._skipping and data.strip():
            self._chunks.append(data)

    def text(self) -> str:
        raw = "".join(self._chunks)
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n\s*\n\s*\n+", "\n\n", raw)
        return raw.strip()


def _http_fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "text/html"})
    with urlopen(req, timeout=30) as resp:  # noqa: S310 - user-supplied URL is intended
        charset = resp.headers.get_content_charset() or "utf-8"
        html = resp.read().decode(charset, errors="replace")
    parser = _TextExtractor()
    parser.feed(html)
    return parser.text()


def _browser_fetch(url: str) -> str:
    from playwright.sync_api import sync_playwright  # imported lazily

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(user_agent=_USER_AGENT)
            page.goto(url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(1500)
            return page.inner_text("body")
        finally:
            browser.close()


def fetch_jd(url: str) -> JobPosting:
    host_is_js = any(h in url.lower() for h in JS_HEAVY_HOSTS)

    if not host_is_js:
        try:
            text = _http_fetch(url)
            if len(text) >= 600:
                return JobPosting(url=url, text=text, method="http")
        except Exception:  # noqa: BLE001 - fall through to the browser
            pass

    # JS-heavy host, thin HTTP result, or an HTTP error: use the browser.
    text = _browser_fetch(url)
    return JobPosting(url=url, text=text, method="browser")


def load_jd_from_file(path: str) -> JobPosting:
    """For offline testing: treat a local file as the JD text."""
    from pathlib import Path

    text = Path(path).read_text(encoding="utf-8")
    return JobPosting(url=f"file://{path}", text=text, method="file")
