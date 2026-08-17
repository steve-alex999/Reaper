# Resume Rules & LaTeX Template

## Absolute formatting rules
1. **No em dashes (—)** anywhere in any resume.
2. **No double hyphens (--)** in resume body or bullets. Break into separate sentences with periods.
3. **No personal or invented projects.** Only the 4 repos in GITHUB_REPOS.md.
4. **Education is locked** — never change dates or degrees.
5. Every bullet quantified where possible, using the metrics in CLAUDE.md.
6. Be honest — no fabricated tools, depth, or titles. Mark learning-level skills as "(learning, <source>)".

## Compact skills format (LOCKED)
Minimize `\\ &` continuation breaks. Keep a category's items flowing on one line; only wrap to a new `& ` line when the line would overflow the page margin. Start a new `\\` row only for a genuinely new category.

```latex
\begin{rSection}{Skills}
\begin{tabular}{ @{} >{\bfseries}l @{\hspace{4ex}} l }
Category One   & Item A, Item B, Item C, Item D, Item E, \\
               & Item F, Item G (wrap only when line overflows) \\
Category Two   & Item A, Item B, Item C, Item D, Item E, Item F \\
Category Three & Item A, Item B, Item C \\
\end{tabular}
\end{rSection}
```

## Standard preamble
```latex
\documentclass{resume}
\usepackage[left=0.3 in,top=0.2in,right=0.3 in,bottom=0.2in]{geometry}
\newcommand{\tab}[1]{\hspace{.04\textwidth}\rlap{#1}}
\newcommand{\itab}[1]{\hspace{0em}\rlap{#1}}
\name{Stephen Guzzarlapudi}
\address{443 388 4998 \textbar{} Baltimore, MD}
\address{\href{mailto:stephensugun999@gmail.com}{stephensugun999@gmail.com} \textbar{} \href{https://linkedin.com/in/stephen-guzz}{linkedin.com/in/stephen-guzz} \textbar{} \href{https://github.com/steve-alex999}{github.com/steve-alex999}}
\begin{document}
% ... sections: Summary, Education, Experience, Projects, Skills ...
\end{document}
```

## Section conventions
- Order: Summary → Education → Experience → Projects → Skills.
- Community Dreams EPM role appears first in Experience (most recent, March 2026–Present), tailored to the target role.
- Use `\vspace{-4mm}` between major sections and `\vspace{-2mm}` between bullets, matching existing resumes.
- The ICICI job title is reframed per role (e.g., "Security Engineer", "AI/ML Software Engineer", "Frontend Software Engineer", "Software Engineer — Entitlements and IAM Platform"). Keep the reframe honest — the underlying work supports it.

## Cover letter rules (when requested)
- P1: name company + role, reference one specific real thing about the company (blog, product, news). Not generic.
- P2: 2–3 strongest requirement matches, each with one concrete metric.
- P3: address the biggest gap head-on, honestly. Don't pretend it doesn't exist.
- Closing: one sentence asking for the interview. No "I look forward to the opportunity to discuss."
- Under 250 words. Confident, specific, human. Build as .docx (see docx skill).
