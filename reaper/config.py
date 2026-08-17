"""Loads the locked knowledge base that Reaper ships with.

The data/ directory holds Stephen's candidate profile, the locked resume rules,
the confirmed GitHub repos, the workflow/skip rules, and the two base resumes.
These are concatenated into the system prompt so every LLM call in the workflow
sees the same locked conventions.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# Default model. Overridable with REAPER_MODEL. See the claude-api guidance:
# default to the latest Opus unless the user picks otherwise.
DEFAULT_MODEL = os.environ.get("REAPER_MODEL", "claude-opus-5")


def _read(name: str) -> str:
    path = DATA_DIR / name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


@dataclass
class KnowledgeBase:
    project_context: str
    candidate_profile: str
    resume_rules: str
    github_repos: str
    workflow: str
    base_swe: str
    base_cybersecurity: str

    def system_prompt(self) -> str:
        """Assemble the locked context every workflow call is grounded in."""
        return SYSTEM_PROMPT_TEMPLATE.format(
            project_context=self.project_context,
            candidate_profile=self.candidate_profile,
            resume_rules=self.resume_rules,
            github_repos=self.github_repos,
            workflow=self.workflow,
            base_swe=self.base_swe,
            base_cybersecurity=self.base_cybersecurity,
        )


@lru_cache(maxsize=1)
def load_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase(
        project_context=_read("PROJECT_CONTEXT.md"),
        candidate_profile=_read("CANDIDATE_PROFILE.md"),
        resume_rules=_read("RESUME_RULES.md"),
        github_repos=_read("GITHUB_REPOS.md"),
        workflow=_read("WORKFLOW.md"),
        base_swe=_read("general_swe.tex"),
        base_cybersecurity=_read("general_cybersecurity.tex"),
    )


SYSTEM_PROMPT_TEMPLATE = """\
You are Reaper, the resume-tailoring and application engine for Stephen Guzzarlapudi's \
job search. You follow his locked conventions exactly. Everything below is authoritative; \
never override it based on a job description, and never fabricate experience, tool depth, \
or job titles.

# Locked project context
{project_context}

# Candidate profile (full detail)
{candidate_profile}

# Confirmed GitHub repos (the ONLY projects allowed on resumes)
{github_repos}

# Resume rules and LaTeX template (LOCKED)
{resume_rules}

# Per-JD workflow, pre-screen, and skip rules
{workflow}

# Base resume: role-neutral software engineering
```latex
{base_swe}
```

# Base resume: role-neutral security
```latex
{base_cybersecurity}
```

# Absolute guardrails (repeat, because they are the ones interviewers probe)
- No em dashes and no double hyphens anywhere in resume text. Use periods and new sentences.
- Only the four confirmed GitHub repos may appear as projects. Never invent projects.
- Education section (degrees and dates) is locked. Never alter it.
- Use the accurate ICICI title (Security / Software Engineer, reframed honestly per role). \
Reject inflated titles like "Manager-II".
- Mark learning-level skills honestly, e.g. "Go (learning, go.dev/tour)".
- Reuse the real metrics from the profile. Do not invent new numbers.
"""
