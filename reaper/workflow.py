"""The locked three-prompt workflow, run as one cached conversation.

  Prompt 1 - Recruiter analysis: score /100, keywords, red flags, verdict.
  Prompt 2 - Experience rewrite: ICICI + NIC + Community Dreams bullets in the
             JD's vocabulary, XYZ format, quantified.
  Prompt 3 - ATS check + final compile-ready LaTeX resume.

Plus a screener-answer pass that feeds the application answer pack.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from reaper.config import load_knowledge_base
from reaper.llm import Conversation
from reaper.prescreen import PreScreen

ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "company": {"type": "string"},
        "role_title": {"type": "string"},
        "match_score": {"type": "integer"},
        "fit_band": {
            "type": "string",
            "enum": ["strong", "viable", "stretch", "skip"],
        },
        "top_keywords": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "keyword": {"type": "string"},
                    "present_in_profile": {"type": "boolean"},
                },
                "required": ["keyword", "present_in_profile"],
            },
        },
        "red_flags": {"type": "array", "items": {"type": "string"}},
        "strong_sections": {"type": "array", "items": {"type": "string"}},
        "weak_sections": {"type": "array", "items": {"type": "string"}},
        "verdict": {"type": "string", "enum": ["apply", "apply_with_caveat", "skip"]},
        "verdict_reason": {"type": "string"},
        "resume_base": {"type": "string", "enum": ["swe", "cybersecurity"]},
    },
    "required": [
        "company", "role_title", "match_score", "fit_band", "top_keywords",
        "red_flags", "strong_sections", "weak_sections", "verdict",
        "verdict_reason", "resume_base",
    ],
}

SCREENER_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "why_this_company": {"type": "string"},
        "why_this_role": {"type": "string"},
        "biggest_gap_answer": {"type": "string"},
        "strongest_match": {"type": "string"},
        "short_cover_note": {"type": "string"},
    },
    "required": [
        "why_this_company", "why_this_role", "biggest_gap_answer",
        "strongest_match", "short_cover_note",
    ],
}


@dataclass
class WorkflowResult:
    analysis: dict
    experience_rewrite: str
    resume_tex: str
    ats_notes: str
    screener: dict


def _prompt1(prescreen: PreScreen, jd: str) -> str:
    return f"""\
Run PROMPT 1 of the three-prompt workflow: the recruiter analysis.

Reaper already ran the deterministic pre-screen. Its findings:
{prescreen.summary()}

Here is the full job description:
<job_description>
{jd}
</job_description>

Score the fit /100 using the scoring calibration in the workflow rules (76 was the
highest role analysed; 70-74 strong; 62-68 viable with a named gap; 58 and below a
stretch/pivot; under 50 or a hard blocker means skip). Pick the honest resume base
('swe' or 'cybersecurity'). Identify the top ATS keywords and whether each is truly
supported by Stephen's profile. Give three real red flags, the strong and weak parts of
his fit, and a verdict. Be honest about gaps; interviewers probe claims."""


def _prompt2(jd: str) -> str:
    return f"""\
Run PROMPT 2: the experience rewrite.

Rewrite Stephen's ICICI Bank, NIC internship, and Community Dreams bullets in THIS role's
vocabulary. Use XYZ format (accomplished X, measured by Y, by doing Z), quantified with his
real metrics only. Reframe the ICICI title honestly for this role. Do not invent tools,
depth, or numbers. Keep the Community Dreams role first (most recent). Output the rewritten
bullets grouped by role, ready to drop into the LaTeX Experience section.

Reminder of the target role:
<job_description>
{jd}
</job_description>"""


def _prompt3(base_choice: str) -> str:
    return f"""\
Run PROMPT 3: the ATS + hiring-manager check, then the final resume.

First give a short ATS + hiring-manager checklist: which target keywords are now covered,
any that are still missing and why that is acceptable, and the honest gaps to expect in an
interview.

Then output the COMPLETE, compile-ready LaTeX resume, tailored to this role, starting from
the '{base_choice}' base and folding in the rewritten Experience bullets, a tailored Summary,
and a tailored Skills block. Follow every locked rule in the resume rules: no em dashes, no
double hyphens in the body, only the four confirmed repos, locked education, the compact
skills format, and the standard `resume` document class preamble.

Wrap the LaTeX in a single fenced block exactly like this so it can be extracted:
```latex
<full document from \\documentclass to \\end{{document}}>
```
Put the ATS checklist BEFORE the fenced LaTeX block."""


def _screener_prompt(jd: str) -> str:
    return f"""\
Now produce short, honest answers to the application's common screener questions, in
Stephen's voice: confident, specific, human, no fabrication. Ground "why this company" in one
real, specific thing about the employer from the JD (a product, team, or stated mission).
Address the biggest gap head-on. Keep each answer tight (2-4 sentences); the short cover note
is under 120 words. Use the standing sponsorship answer verbatim only if the question asks
about work authorization; otherwise do not raise it.

<job_description>
{jd}
</job_description>"""


def _extract_latex(text: str) -> tuple[str, str]:
    """Return (latex, notes_before_the_block)."""
    m = re.search(r"```latex\s*(.*?)```", text, re.DOTALL)
    if m:
        latex = m.group(1).strip()
        notes = text[: m.start()].strip()
        return latex, notes
    # Fallback: grab from \documentclass to \end{document}.
    m = re.search(r"(\\documentclass.*?\\end\{document\})", text, re.DOTALL)
    if m:
        return m.group(1).strip(), text[: m.start()].strip()
    return "", text.strip()


def _manual_prompt3() -> str:
    return (
        _prompt3("the base you chose in step 1 (swe or cybersecurity)")
        + "\n\nIf you have not already, state which base you picked before the resume."
    )


def build_prompt_bundle(jd_text: str, prescreen: PreScreen) -> dict[str, str]:
    """Assemble the manual, API-free prompt bundle.

    Returns a filename -> content map: the locked system prompt plus the four
    step prompts, each pre-filled with this JD. Paste them into any chat UI
    (e.g. free claude.ai) in order; no API call is made here.
    """
    kb = load_knowledge_base()
    return {
        "00_SYSTEM_PROMPT.md": (
            "Paste this ONCE as the first message (or as a Project/custom "
            "instruction), then send the numbered prompts in order.\n\n"
            + kb.system_prompt()
        ),
        "01_recruiter_analysis.md": _prompt1(prescreen, jd_text),
        "02_experience_rewrite.md": _prompt2(jd_text),
        "03_ats_resume.md": _manual_prompt3(),
        "04_screener_answers.md": _screener_prompt(jd_text),
        "README.md": (
            "# Manual (no-API) workflow\n\n"
            "1. Open a fresh chat at claude.ai (or any capable LLM).\n"
            "2. Paste `00_SYSTEM_PROMPT.md` as the first message.\n"
            "3. Send `01`, then `02`, then `03`, then `04`, in order, each as a "
            "new message in the same chat.\n"
            "4. Save the LaTeX from step 03 to `resume.tex`.\n"
            "5. Compile it: `reaper compile resume.tex`.\n"
            "6. Use the identity block from `answer_pack.md` plus your step-04 "
            "answers to fill the form (or paste them into the ATS).\n"
        ),
    }


def run_workflow(
    jd_text: str, prescreen: PreScreen, model: str | None = None
) -> WorkflowResult:
    kb = load_knowledge_base()
    convo = Conversation(kb.system_prompt(), model=model)

    analysis = convo.ask_json(_prompt1(prescreen, jd_text), ANALYSIS_SCHEMA)
    experience = convo.ask_text(_prompt2(jd_text), max_tokens=6000)
    base = analysis.get("resume_base", "swe")
    resume_raw = convo.ask_text(_prompt3(base), max_tokens=16000)
    resume_tex, ats_notes = _extract_latex(resume_raw)
    screener = convo.ask_json(_screener_prompt(jd_text), SCREENER_SCHEMA)

    return WorkflowResult(
        analysis=analysis,
        experience_rewrite=experience,
        resume_tex=resume_tex,
        ats_notes=ats_notes,
        screener=screener,
    )
