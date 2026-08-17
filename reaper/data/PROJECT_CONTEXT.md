# CLAUDE.md — Job Search Project Context

This file orients Claude Code for Stephen Guzzarlapudi's job-search work. Read it fully before helping with any resume, cover letter, or interview task. Detailed context lives in `docs/`.

---

## What this repo is for

Tailoring resumes and cover letters per job description, tracking applications, and preparing for interviews. The workflow, formatting rules, and candidate facts below are **locked conventions** — follow them exactly unless Stephen says otherwise.

---

## Candidate snapshot

- **Name:** Stephen Guzzarlapudi
- **Contact:** 443-388-4998 | stephensugun999@gmail.com | linkedin.com/in/stephen-guzz | github.com/steve-alex999
- **Location:** Baltimore, MD
- **Work auth:** F-1 STEM OPT (~3 years runway, to ~Dec 2028). Needs H-1B sponsorship afterward.
- **Education:** MS Security Informatics, Johns Hopkins (Aug 2024–Dec 2025) · B.Tech CS&E, IIT Ropar (Aug 2018–May 2022)
- **Certs:** CEH (EC-Council), CISP (NFSU)
- **Experience:** ICICI Bank, security/software engineer, Mumbai (June 2022–July 2024) · NIC internship, Hyderabad (May–July 2021)
- **Current:** Volunteer Executive Project Manager, Community Dreams Foundation (since **March 2026**) — FinAccruals/LedgerFlow: Office.js Excel add-in, React/TypeScript + Python + Supabase, QuickBooks/Xero integration.

Full detail: `docs/CANDIDATE_PROFILE.md`

---

## Resume formatting rules (LOCKED — never violate)

1. **No em dashes** (—) anywhere.
2. **No double hyphens** (--) in resume body/bullets. Use periods and new sentences.
3. **No personal/invented projects.** Only the 4 confirmed GitHub repos (see `docs/GITHUB_REPOS.md`).
4. **Compact skills format.** Minimize `\\ &` line breaks; keep items flowing on one line, wrap to a new `& ` continuation line only when the line overflows the margin. Template in `docs/RESUME_RULES.md`.
5. **Education is locked** — do not alter dates or degrees.
6. LaTeX uses the `resume` document class. Standard preamble in `docs/RESUME_RULES.md`.

---

## Per-JD workflow (the "three-prompt" method)

For each new job description, produce in order:
1. **Recruiter analysis** — match score /100, keyword check, red flags, strengths/weaknesses, verdict.
2. **Experience rewrite** — ICICI/NIC bullets rewritten in the JD's vocabulary (XYZ format, quantified).
3. **ATS + hiring-manager check + final LaTeX resume.**

Always run a **pre-screen first**: check sponsorship language, location, salary, citizenship/clearance requirements, and whether it's a staffing firm. Details in `docs/WORKFLOW.md`.

---

## Hard rules on what to skip

- **No-sponsorship** employers (permanent skip list in `docs/WORKFLOW.md`).
- **Staffing firms** ("our client", "W2", "I'm recruiting for", unnamed employer).
- **Citizenship/clearance** roles (Secret, TS/SCI, ITAR, "US citizen required").
Always be honest about gaps — never fabricate experience, tool depth, or titles. Interviewers probe claims.

---

## Key reusable metrics

2M+ daily transactions · 120+ incidents · 45% MTTR reduction · 85% unauthorized-access reduction · 95% critical-vuln reduction · 55% overhead reduction · 99.7% uptime · 14 enterprise apps · 9 microservices · 6 full-stack apps · 40% faster releases · 65% DB latency reduction · 400+ NIC users · 8,000+ NIC records.

---

## Standing guidance

- **Sponsorship answer (interviews):** "I am currently authorized to work on F-1 STEM OPT, which provides three years of work authorization without requiring any sponsorship. After that period I would require H-1B sponsorship to continue."
- **Honesty on titles:** Use the accurate ICICI title (security/software engineer). Do NOT use inflated titles like "Manager-II" that appear in some third-party docs — title mismatches vs LinkedIn are a red flag.
- Base resumes ready to tailor: `resumes/general_swe.tex`, `resumes/general_cybersecurity.tex`.

---

## Current status & next actions

See `docs/STATUS.md` for the live pipeline, submission tracker, and open threads. **Top priority: IBM SOC (score 76, highest of all analyzed roles) is resume-ready but unsubmitted.**
