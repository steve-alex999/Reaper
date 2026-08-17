"""Step 0 pre-screen: the deterministic ctrl+F checks Reaper runs before any
LLM work. Mirrors docs/WORKFLOW.md. Flags hard blockers (no sponsorship,
citizenship/clearance) and soft flags (staffing firm, salary, years), so a role
that should be skipped never burns an LLM pass.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Employers that have confirmed no sponsorship (permanent skip list).
NO_SPONSORSHIP_EMPLOYERS = (
    "epic systems", "milliman", "pwc", "elsevier", "datasite", "phenom",
)

# Ambiguous on sponsorship: verify before investing.
VERIFY_SPONSORSHIP_EMPLOYERS = (
    "abnormal", "affirm", "aledade", "klaviyo", "precisely", "vanta", "toast",
    "smartsheet", "chainalysis", "dtcc", "globus", "blackrock", "mitre",
    "fisher investments",
)

_NO_SPONSORSHIP_PATTERNS = (
    r"will not (provide|offer|sponsor)",
    r"unable to (provide|offer) sponsorship",
    r"no(t)?\s+(able to )?sponsor",
    r"without (the need for )?(immigration|visa) sponsorship",
    r"do(es)? not sponsor",
    r"sponsorship is not (available|offered|provided)",
    r"not (be )?(able|eligible) (to|for).{0,40}sponsor",
    r"now or in the future",
    r"authorized to work.{0,40}without sponsorship",
)

_CLEARANCE_PATTERNS = (
    r"\bu\.?s\.? citizen(ship)?\b.{0,40}(required|only)",
    r"must be a (u\.?s\.? )?citizen",
    r"security clearance",
    r"\bsecret\b", r"ts/sci", r"top secret", r"\bitar\b", r"\bear\b",
    r"public trust",
)

_STAFFING_PATTERNS = (
    r"our client", r"i'?m recruiting for", r"in partnership with",
    r"\bw2\b", r"c2c", r"corp to corp", r"third[- ]party",
)


@dataclass
class PreScreen:
    hard_blockers: list[str] = field(default_factory=list)
    soft_flags: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    salary: str | None = None
    years_required: str | None = None

    @property
    def should_skip(self) -> bool:
        return bool(self.hard_blockers)

    def summary(self) -> str:
        lines = []
        if self.hard_blockers:
            lines.append("HARD BLOCKERS (recommend SKIP):")
            lines += [f"  - {b}" for b in self.hard_blockers]
        if self.soft_flags:
            lines.append("Flags to verify:")
            lines += [f"  - {f}" for f in self.soft_flags]
        if self.salary:
            lines.append(f"Salary: {self.salary}")
        if self.years_required:
            lines.append(f"Years required: {self.years_required} (Stephen has ~2)")
        if self.notes:
            lines.append("Notes:")
            lines += [f"  - {n}" for n in self.notes]
        if not lines:
            lines.append("No pre-screen blockers found.")
        return "\n".join(lines)


def _any(patterns, text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _find_salary(text: str) -> str | None:
    m = re.search(
        r"\$\s?\d{2,3}(?:,\d{3})?(?:\s?[kK])?\s?(?:-|to|–)\s?\$?\s?\d{2,3}(?:,\d{3})?(?:\s?[kK])?",
        text,
    )
    return m.group(0) if m else None


def _find_years(text: str) -> str | None:
    m = re.search(r"(\d{1,2})\+?\s*(?:-\s*\d{1,2}\s*)?years?", text, re.IGNORECASE)
    return m.group(0) if m else None


def prescreen(jd_text: str) -> PreScreen:
    result = PreScreen()
    low = jd_text.lower()

    for emp in NO_SPONSORSHIP_EMPLOYERS:
        if emp in low:
            result.hard_blockers.append(
                f"Employer '{emp}' is on the permanent no-sponsorship skip list."
            )
    if _any(_NO_SPONSORSHIP_PATTERNS, jd_text):
        result.hard_blockers.append(
            "JD language excludes visa sponsorship (Stephen needs H-1B after OPT)."
        )
    if _any(_CLEARANCE_PATTERNS, jd_text):
        result.hard_blockers.append(
            "Citizenship / clearance / export-control requirement detected."
        )

    if _any(_STAFFING_PATTERNS, jd_text):
        result.soft_flags.append(
            "Looks like a staffing firm (our client / W2 / C2C). Chase the employer "
            "name, salary, and sponsorship before applying."
        )
    for emp in VERIFY_SPONSORSHIP_EMPLOYERS:
        if emp in low:
            result.soft_flags.append(
                f"Employer '{emp}' is on the sponsorship VERIFY-FIRST list."
            )

    result.salary = _find_salary(jd_text)
    if not result.salary:
        result.notes.append("No salary range found in the posting.")
    result.years_required = _find_years(jd_text)

    return result
