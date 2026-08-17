# Per-JD Workflow, Pre-Screen & Skip Rules

## Step 0 — Pre-screen (do this BEFORE any analysis)
Check the JD for:
- **Sponsorship language.** Ctrl+F: "sponsorship", "without immigration support", "now or in the future", "H-1B lottery", "citizenship", "clearance", "Secret", "TS/SCI", "ITAR", "EAR", "legally authorized ... ongoing". If it excludes sponsorship or requires citizenship/clearance → SKIP.
- **Staffing firm?** Patterns: "our client", "I'm recruiting for", "in partnership with", "W2", unnamed employer, generic keyword-stuffed skill lists, no product/team described, no salary. → SKIP unless Stephen wants to chase the employer name/salary/sponsorship.
- **Location.** Note vs Baltimore MD. Flag relocation/onsite.
- **Salary range.** Note if present.
- **Years required** vs Stephen's ~2 years.

## The three-prompt method (per viable JD)
1. **Recruiter analysis (rendered as a visual widget in chat):** score /100, keyword status, top-5 ATS keywords, 3 red flags, strong/weak sections, profile-vs-role comparison, verdict.
2. **Experience rewrite:** ICICI + NIC (+ Community Dreams) bullets rewritten in the JD's vocabulary, XYZ format, quantified.
3. **ATS + hiring-manager check + final LaTeX resume** following RESUME_RULES.md.

## Scoring calibration (from this thread)
- 76 = IBM SOC (highest analyzed). 70–74 = strong (Abnormal AI 74, Google PRISM 74, FedEx 73, Affirm 73, JPMorgan AI/ML 70, Walmart UEBA 72, Cisco Meraki 72, Aledade 72).
- 62–68 = viable, usually with a named gap or pending verification (Goldman Entitlements 68, Precisely 68, MITRE 68, JPMorgan variants, Smartsheet 62, Chainalysis 62 career-pivot).
- 58 and below = stretch/pivot (Fisher documentation 58).
- <50 or hard-blocker = skip.

## Permanent NO-SPONSORSHIP skip list
Epic Systems, Milliman, PwC, Elsevier, Datasite, Phenom. (Verify Washington Post / Nash Holdings separately.)

## Sponsorship VERIFY-FIRST list (ambiguous, ask before investing)
Abnormal AI, Affirm, Aledade, Klaviyo, Precisely, Vanta, Toast, Smartsheet, Chainalysis, DTCC, Globus, BlackRock, MITRE, Fisher Investments.

## Honesty guardrails
- Never fabricate tool depth, experience, or job titles.
- Mark learning-level skills honestly: "Go (learning, go.dev/tour)", "Streamlit (hands-on)", etc.
- Use accurate ICICI title. Reject inflated titles (e.g., "Cyber Security Manager-II") from third-party docs.
