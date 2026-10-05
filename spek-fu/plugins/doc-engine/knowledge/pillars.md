# Doc-Engine Pillars

Shared behavioral anchors for all doc-engine skills and agents.

**Terseness** — minimal verbosity, maximal signal. Every layer has hard limits:
- Index entries: 1 sentence description maximum
- Module sections: ≤ 3 sentences, ≤ 5 bullet points per H2 section
- Inline code comments: 1 sentence maximum

**Progressive Disclosure** — avoid loading unnecessary context. Information is layered from coarsest to finest:
1. `spek-fu/project/code-docs/index.json` — quickest lookup; tags and 1-sentence descriptions only
2. Doc modules (`spek-fu/project/code-docs/**/*.md`) — medium detail; section-level summaries
3. Code comments — high detail; granular descriptions inside source files
4. Source code — full detail; last resort

**Deterministic Foundation** — scripts handle traversal, extraction, and validation. AI handles reasoning, writing, and orchestration. Never implement what a script can do reliably or if a script already handles a certain problem.

**AI Augmenting** — AI uses scripts as tools. Scripts produce structured output; AI interprets, writes, and decides.
