"""Assemble the ready-to-paste application answer pack.

Deterministic identity fields come straight from the candidate profile; the
tailored screener answers come from the workflow's LLM pass. The result is a
single Markdown sheet the user pastes into whatever ATS the link uses, and a
machine-readable dict the autofill module maps onto real form fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Locked identity facts (mirror docs/CANDIDATE_PROFILE.md). These never come from
# the LLM so they can never drift.
IDENTITY = {
    "first_name": "Stephen",
    "last_name": "Guzzarlapudi",
    "full_name": "Stephen Guzzarlapudi",
    "email": "stephensugun999@gmail.com",
    "phone": "443-388-4998",
    "location": "Baltimore, MD",
    "linkedin": "https://linkedin.com/in/stephen-guzz",
    "github": "https://github.com/steve-alex999",
    "work_authorization": "Authorized to work on F-1 STEM OPT (about 3 years, through ~Dec 2028).",
    "requires_sponsorship_now": "No",
    "requires_sponsorship_future": "Yes (H-1B after OPT expires).",
}

SPONSORSHIP_ANSWER = (
    "I am currently authorized to work on F-1 STEM OPT, which provides three years "
    "of work authorization without requiring any sponsorship from the employer. "
    "After that period, I would require H-1B sponsorship to continue working in the US."
)


@dataclass
class AnswerPack:
    company: str
    role_title: str
    identity: dict = field(default_factory=lambda: dict(IDENTITY))
    sponsorship_answer: str = SPONSORSHIP_ANSWER
    screener: dict = field(default_factory=dict)

    def to_markdown(self, resume_pdf: str | None) -> str:
        s = self.screener
        lines = [
            f"# Application answer pack: {self.company} - {self.role_title}",
            "",
            "Paste these into the form fields. Identity fields are locked; screener",
            "answers are tailored to this role.",
            "",
            "## Identity and contact",
            f"- Full name: {self.identity['full_name']}",
            f"- First / last: {self.identity['first_name']} / {self.identity['last_name']}",
            f"- Email: {self.identity['email']}",
            f"- Phone: {self.identity['phone']}",
            f"- Location: {self.identity['location']}",
            f"- LinkedIn: {self.identity['linkedin']}",
            f"- GitHub: {self.identity['github']}",
            "",
            "## Work authorization",
            f"- Authorized to work now: Yes. {self.identity['work_authorization']}",
            f"- Need sponsorship now: {self.identity['requires_sponsorship_now']}",
            f"- Need sponsorship in future: {self.identity['requires_sponsorship_future']}",
            "",
            "Standing answer to \"do you now or will you require sponsorship\":",
            f"> {self.sponsorship_answer}",
            "",
            "## Resume",
            f"- Attach: {resume_pdf or 'resume.tex (compile to PDF first)'}",
            "",
            "## Screener answers (tailored)",
            f"**Why this company?**\n{s.get('why_this_company', '')}",
            "",
            f"**Why this role?**\n{s.get('why_this_role', '')}",
            "",
            f"**Strongest match to the requirements:**\n{s.get('strongest_match', '')}",
            "",
            f"**Biggest gap, addressed honestly:**\n{s.get('biggest_gap_answer', '')}",
            "",
            "## Short cover note (paste into a cover-letter box)",
            s.get("short_cover_note", ""),
            "",
        ]
        return "\n".join(lines)

    def field_map(self) -> dict[str, str]:
        """Flat name->value map the autofill module matches against form labels."""
        s = self.screener
        return {
            "first name": self.identity["first_name"],
            "last name": self.identity["last_name"],
            "full name": self.identity["full_name"],
            "name": self.identity["full_name"],
            "email": self.identity["email"],
            "phone": self.identity["phone"],
            "location": self.identity["location"],
            "city": "Baltimore",
            "linkedin": self.identity["linkedin"],
            "github": self.identity["github"],
            "website": self.identity["github"],
            "sponsorship": self.sponsorship_answer,
            "authorized": "Yes",
            "why": s.get("why_this_company", ""),
            "cover": s.get("short_cover_note", ""),
        }


def build_answer_pack(company: str, role_title: str, screener: dict) -> AnswerPack:
    return AnswerPack(company=company, role_title=role_title, screener=screener)
