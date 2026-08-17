# Reaper

**Reaper** reaps a job-application link into a finished application. Paste a URL and it:

1. **Fetches** the job description (plain HTTP, with a Playwright browser fallback for JS-heavy ATS pages like Workday/LinkedIn).
2. **Pre-screens** it deterministically (Step 0): no-sponsorship language, citizenship/clearance requirements, staffing-firm tells, salary, and years required — so a role that should be skipped never burns an LLM pass.
3. Runs Stephen Guzzarlapudi's locked **three-prompt workflow** to build a custom resume:
   - **Prompt 1 – Recruiter analysis**: match score /100, top ATS keywords (with which ones his profile actually supports), red flags, strong/weak sections, and a verdict.
   - **Prompt 2 – Experience rewrite**: ICICI, NIC, and Community Dreams bullets rewritten in the JD's vocabulary, XYZ format, quantified with real metrics only.
   - **Prompt 3 – ATS + hiring-manager check + final LaTeX resume**, following every locked resume rule.
4. **Compiles** the resume to PDF (tectonic / latexmk / pdflatex; falls back to `.tex` only).
5. Builds a ready-to-paste **answer pack**: locked identity/contact/work-auth fields plus tailored screener answers ("why this company", biggest-gap answer, short cover note).
6. **Auto-fills** the form in a real browser on supported ATS platforms (Greenhouse, Lever), pausing for you to review — **it never submits** — and falls back to the paste sheet everywhere else.

All the locked context (candidate profile, resume rules, the four confirmed GitHub repos, skip lists, base resumes) ships in `reaper/data/` and grounds every LLM call.

## Install

```bash
pip install -e .
# For JD fetching on JS-heavy sites and browser auto-fill:
pip install playwright   # Chromium is already present in the Reaper web env
```

Set your key (the app calls the Claude API):

```bash
export ANTHROPIC_API_KEY=sk-ant-...    # or run `ant auth login`
```

## Use

```bash
# Full pipeline on a pasted link
reaper apply "https://boards.greenhouse.io/acme/jobs/12345"

# Just the deterministic pre-screen, no LLM
reaper prescreen "https://jobs.lever.co/acme/abc-123"

# Skip the browser entirely (answer pack + resume only)
reaper apply "<url>" --no-autofill

# Work from a saved JD file offline (no fetch, no autofill)
reaper apply --jd-file jd.txt
```

## Use without the Claude API (no key, no cost)

The tailoring itself needs an LLM, but you don't have to pay for API calls — run the
same three-prompt workflow in the free claude.ai chat and let Reaper handle the
deterministic scaffolding:

```bash
# 1. Generate a ready-to-paste prompt bundle (no API call is made)
reaper prompts "<url>"        # or: reaper prompts --jd-file jd.txt

# 2. Open a fresh chat at claude.ai. Paste prompts/00_SYSTEM_PROMPT.md first,
#    then send 01, 02, 03, 04 in order (see prompts/README.md).

# 3. Save the LaTeX from step 03 to resume.tex, then compile it:
reaper compile resume.tex
```

`reaper prompts` writes `applications/manual-<date>/` with the JD, the pre-screen,
the `prompts/` bundle (system prompt + the four step prompts pre-filled with your
JD), and `answer_pack.md` with the static identity/work-auth fields. The `prescreen`
command and the base resumes in `reaper/data/` are also fully offline.

## Use with the Claude API (fully automated)

Every `apply` run writes `applications/<company>-<role>-<date>/` containing:

| File | What it is |
|------|-----------|
| `jd.txt` | the fetched job description |
| `prescreen.txt` | Step-0 findings |
| `analysis.json` | recruiter analysis + score |
| `experience_rewrite.md` | rewritten bullets |
| `ats_notes.md` | ATS + hiring-manager checklist |
| `resume.tex` / `resume.pdf` | the tailored resume |
| `answer_pack.md` | everything to paste into the form |

## Configuration

- `ANTHROPIC_API_KEY` — required for `apply`.
- `REAPER_MODEL` — override the Claude model (default `claude-opus-5`).

## Guardrails (enforced by the system prompt)

No em dashes or double hyphens in resume text, only the four confirmed GitHub repos, locked education, honest ICICI title and skill levels, and real metrics only. Reaper never fabricates experience, and never submits an application for you.
