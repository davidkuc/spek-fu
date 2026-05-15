---
id: skf-knowledge-skill-design-guide
description: "Unified skill authoring, design, and validation reference. Covers the V2.0 8-section U-shape structure, frontmatter schema, design principles, authoring workflow, common pitfalls, language conventions, reusable patterns, and a complete check/fix validation catalogue. Consult when authoring, reviewing, or refining any skill in the AI framework."
deprecated: false
version: 1.0
---

# Skill Design Guide

> Unified reference for authoring, reviewing, and refining skills in the skf framework.

⚠️ **This file must always be read in its entirety.** Read successive `read_file` ranges until end of file is confirmed. Stopping early will silently omit rules from evaluation or validation passes.

---

## 1. Why Structure Matters — The Attention Gradient Principle

The V2.0 skill format is built on a single cognitive principle: **U-shaped attention**.

Information embedded in the middle of long passages is missed at higher rates than information at the beginning or end. When agents read skill files, critical rules and workflow steps buried in the middle of prose are inconsistently retained and applied. This produces scope violations, constraint drift, tool misuse, and output variance.

The 8-section U-shape structure concentrates the **highest-signal information at the opening and closing positions** where attention is strongest:

- **Sections 1–3** (top): What the skill does, non-negotiable constraints, and behavioral anchors — everything an agent needs before stepping through a workflow.
- **Sections 4–5** (middle): The detailed workflow and tool policies — full procedural content benefiting from the guardrails established above.
- **Sections 6–8** (bottom): Exact output format, examples, and critical reminders — repeated constraints for recency effect, ensuring the most important rules are read last.

---

## 2. The V2.0 Skill Structure — Canonical Format

Every compliant skill file must follow this exact structure in this order.

**8-section quick reference** (minimum content per section):

| § | XML Tag | Minimum content |
|---|---------|-----------------|
| 1 | (identity block) | 1-paragraph purpose + **Scope boundary** sentence |
| 2 | `<constraints>` | `IMPORTANT:` header + ≥3 NEVER/ALWAYS rules each with `— WHY:` |
| 3 | `<behavioral_anchors>` | Environment Preflight subsection + Operational Anchors with anti-drift clause and self-check |
| 4 | `<workflow>` | `## Preflight` + `## Done conditions` + numbered `## Step N — Title` sections |
| 5 | `<tools>` | Every tool used in the workflow; one-line usage policy each |
| 6 | `<output_format>` | Standard field table + named operation-specific templates |
| 7 | `<examples>` | ≥2 positive demonstrations + ≥1 `type="counter"` counter-example |
| 8 | `<reminders>` | `## Rules` block restating 2–4 critical prohibitions from Section 2 |

**Canonical format template**:

```markdown
---
id: "[skill-slug]"
recommended-tier: "[fast-agent | standard-agent | large-context-agent]"
version: 1.0
description: "[Verb] [object], [output]. USE FOR: [trigger]. DO NOT USE FOR: [exclusions]."
anti-scope: "[What this skill does NOT do — mirroring the exclusion in description.]"
tags:
  - "[primary-category-tag]"
  - "[secondary-tag]"
inputs:
  - "[Description of required input 1 (required)]"
  - "[Description of optional input 2 (optional)]"
outputs:
  - "[Description of output 1]"
  - "[Description of output 2]"
dispatch-variant: "[full | compact]"
---

(If skill is interactive, asks questions to user etc.)
> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions and cannot interact with user when dispatched as a stateless subagent.

# Skill: [skill-slug]

<!-- SECTION 1: Identity (primacy position) -->
[One-paragraph summary: what the skill does, what it produces, when to consult it.]

**Scope boundary**: This skill [scope statement]. It does NOT [excluded action]. For [excluded action], use [sibling-skill-slug].

<!-- SECTION 2: Non-negotiable constraints -->
<constraints>
IMPORTANT: These rules override all other instructions and apply throughout every step.
1. NEVER [primary prohibition] — WHY: [rationale].
2. NEVER [secondary prohibition] — WHY: [rationale].
3. ALWAYS [required gate] — WHY: [rationale].
4. When [predictable failure condition], [specific fallback action].
</constraints>

<!-- SECTION 3: Behavioral anchors -->
<behavioral_anchors>

## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Operational Anchors
- Before producing any output, verify your output complies with all rules in `<constraints>` above.
- Implement EXACTLY and ONLY what this skill defines — no extra features, no unrequested changes.
- If inputs are ambiguous or missing, call `vscode_askQuestions` rather than guessing.
- [Idempotency rule if applicable: detect first-run vs. resume vs. already-complete before acting.]
</behavioral_anchors>

<!-- SECTION 4: Workflow -->
<workflow>

## Preflight

- Resolve any required inputs before reading target files or taking actions.
- Confirm the run state: [not yet started / partially complete / already done].

## Done conditions

- **[primary outcome]** is done when [measurable state — artifact exists, confirmation shown, etc.].
- **[alternate outcome]** is done when [measurable state].

## Step 1 — [First step title]

[Step instructions. Name tools explicitly.]

> **If [predictable failure]**: [specific action to take]

## Step N — [Final step title]

[Step instructions including output template if applicable.]

The skill is complete when [done condition — name the artifact, state, or user confirmation].

</workflow>

<!-- SECTION 5: Tool usage policies -->
<tools>
- **[tool-name]**: [When and how to use it.]
- **[tool-name]**: [When and how to use it.]
- Do NOT use tools not listed here unless the skill explicitly escalates to a sub-skill.
</tools>

<!-- SECTION 6: Output format -->
<output_format>

**Standard Field Table**:

| Field | Value |
|-------|-------|
| status | `ok` \| `blocked` \| `fail` |
| skill_id | `[skill-name]` |
| wave | `N` |
| step | `N.M` |
| output_path | `path/to/artifact or null` |
| summary | one-line summary of what was done |

**Operation-specific output** (add a named block per operation or output type):

```
## [Output Type Title]

[Field 1]: [allowed values or format]
[Field 2]: [allowed values or format]
```

</output_format>

<!-- SECTION 7: Examples -->
<examples>
<example>
Input: [realistic input description]
Expected behavior: [what the skill does and produces]
</example>

<example>
Input: [second realistic input — different case]
Expected behavior: [what the skill does and produces]
</example>

<example type="counter">
Input: [input that should trigger a constraint — scope overreach, missing required field, etc.]
Expected behavior: Skill detects constraint violation. Responds: "[constrained refusal or redirect]."
</example>
</examples>

<!-- SECTION 8: Critical reminders (recency position) -->
<reminders>

## Rules

- **Never [scope overreach prohibition]** — WHY: [rationale].
- **Never [secondary prohibition]** — WHY: [rationale].
- **Always verify** output against `<constraints>` before reporting completion.

</reminders>
```

---

## 3. Section-by-Section Authoring Guidance

### Section 1 — Identity (Primacy Position)

**Purpose**: Establish what the skill does and what it does NOT do in a single scan.

- One paragraph (2–5 sentences) covering: what the skill does, what it produces, and when to consult it.
- A **Scope boundary** sentence naming one adjacent action this skill does NOT do and redirecting to the sibling skill.

One paragraph total; no sub-sections. A clear identity prevents scope creep and misuse.

**Authoring checklist**:
- [ ] Skill purpose is clear in the first sentence
- [ ] Scope boundary explicitly names what this skill does NOT do
- [ ] Redirection to a sibling skill is present for the excluded action

---

### Section 2 — Non-Negotiable Constraints

**Purpose**: State explicit prohibitions that override all other instructions before the workflow runs.

- Each constraint is a NEVER or ALWAYS rule with a `— WHY: [rationale]` suffix.
- Minimum 3 items; ideal 4–6.
- Begin with: `IMPORTANT: These rules override all other instructions and apply throughout every step.`
- Constraints are PROHIBITIONS only. Positive guidance (how to behave, how to prioritize) goes in behavioral anchors.

Agents parse constraints as hard gates before executing other instructions. A prohibition does not get outweighed by competing workflow objectives the way positive guidance does.

**Authoring checklist**:
- [ ] Each rule is phrased as NEVER or ALWAYS (imperative)
- [ ] Each non-trivial rule has a `— WHY:` suffix explaining the business impact
- [ ] Constraints address the highest-risk failure modes for this skill
- [ ] No positive instructions appear here

---

### Section 3 — Behavioral Anchors

**Purpose**: State HOW the agent should behave — its operational philosophy — distinct from WHAT constraints forbid.

- **Environment Preflight** subsection (required): If `env` is `devcontainer`, read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully and apply DCR-01–09 rules before Step 1. If `env` is `host`, no additional action required.
- **Operational Anchors** subsection: 3–5 behavioral heuristics including:
  - The standard compliance self-check: `Before producing any output, verify your output complies with all rules in <constraints> above.`
  - The anti-drift clause: `Implement EXACTLY and ONLY what this skill defines — no extra features, no unrequested changes.`
  - Ambiguity handling guidance (when to ask vs. assume)
  - Idempotency/resumability guidance if the skill can be re-run

**Authoring checklist**:
- [ ] Environment Preflight subsection is present with devcontainer and host branches
- [ ] Operational Anchors subsection has standard compliance self-check
- [ ] Anti-drift clause is present
- [ ] Ambiguity handling is stated (when to ask vs. assume)
- [ ] If the skill can be re-run, includes idempotency guidance

---

### Section 4 — Workflow

**Purpose**: Describe the complete step-by-step process. This is the longest section.

- **Preflight** subsection: resolve required inputs, confirm run state (not yet started / partially complete / already done), and declare any fail-fast conditions before acting.
- **Done conditions** subsection: list one measurable done condition per expected outcome (success path, blocked path, alternate path).
- **Step N — [Title]** subsections: each step numbered and titled.
- **Done condition** at the end of the last step: "The skill is complete when [measurable state]."
- Preserve ALL workflow detail verbatim — steps, sub-steps, tables, decision trees, conditional branches, loops.

Every step requiring user input must route through `vscode_askQuestions`. Steps that write to disk must include an explicit ⛔ STOP gate.

**Do NOT summarize or shorten.** The workflow is the operational specification; agents execute it exactly as written.

**Authoring checklist**:
- [ ] `## Preflight` subsection present — confirms run state and resolves inputs before acting
- [ ] `## Done conditions` subsection present — lists measurable done conditions per outcome
- [ ] Each step has a title and number
- [ ] Sub-steps and branches are clearly marked with `If [condition]...`
- [ ] Done condition in last step is measurable and unambiguous

---

### Section 5 — Tool Usage Policies

**Purpose**: Govern which tools are available and how to use them, preventing misuse and inconsistency.

- One-line description per tool: `**tool-name**: [When and how to use it; key restrictions]`
- Every tool listed must actually be used in the workflow steps above — and every tool used in the workflow must be listed here.
- Include: `Do NOT use tools not listed here unless the skill explicitly escalates to a sub-skill.`
- List tools in order of expected frequency of use.

---

### Section 6 — Output Format

**Purpose**: Define the exact shape of the skill's output to produce consistent, parseable results.

- Start with a standard field table: `status`, `skill_id`, `wave`, `step`, `output_path`, `summary` — with allowed enum values.
- Add named operation-specific blocks (fenced code or markdown) for any human-readable or structured output the skill produces.
- Include all field names, order, and allowed enum values.
- Templates must be complete enough to fill in without guessing.

---

### Section 7 — Examples

**Purpose**: Show agents how the skill behaves in representative scenarios.

- Minimum: 2 positive demonstrations + 1 counter-example.
- Each example shows `Input:` and `Expected behavior:` (both action and output).
- Counter-examples use `type="counter"` and show a constrained refusal or scope boundary enforcement.
- Use realistic inputs, not placeholders like "issue X."

---

### Section 8 — Critical Reminders (Recency Position)

**Purpose**: Repeat the 2–4 most critical constraints from Section 2 for recency effect.

- Bullet list in imperative form: NEVER, ALWAYS.
- The last instruction the agent reads before executing — make it count.
- No new constraints introduced here. Restate from Section 2 only.

---

## 4. Frontmatter Requirements

Every skill file must include YAML frontmatter with all standard fields:

```yaml
---
id: "[skill-slug]"
recommended-tier: "[fast-agent | standard-agent | large-context-agent]"
version: 1.0
description: "[Structured description — see disambiguation rules below.]"
anti-scope: "[One-sentence exclusion boundary matching the description's DO NOT USE FOR clause.]"
tags:
  - "[primary-category-tag]"
  - "[secondary-tag]"
inputs:
  - "[Description of required input (required)]"
  - "[Description of optional input (optional)]"
outputs:
  - "[Description of output 1]"
dispatch-variant: "[full | compact]"
---
```

Skills do not have a `model` field. Model selection is the calling agent's responsibility.

> **Standard required input — `env`**: All skills must include the following `env` entry as the last item in their `inputs:` list:
> ```
> - "env: runtime environment passed by the orchestrator — 'devcontainer' or 'host'"
> ```

### Description Disambiguation Rules

In a multi-plugin workspace, the `description` field is the sole text an agent reads when deciding which skill to consult. A vague or generic description causes misrouting.

**Rule D1 — Lead with action + object.** Start with a verb and a concrete object.
- ✅ "Runs `dotnet test` against discovered test projects and returns a structured summary of results."
- ❌ "Testing skill for running tests."
- ❌ Blocklisted opening verbs: *Handles, Manages, Processes, Provides, Supports, Facilitates, Enables, Maintains, Deals with, Takes care of, Is responsible for.*

**Rule D2 — Name the output.** State what artifact, result, or state change the skill produces.
- ✅ "...returning a structured summary of errors and warnings."
- ❌ "...and gives results."

**Rule D3 — State the trigger condition.** Include a `USE FOR:` clause or equivalent.
- ✅ "USE FOR: generating execution plans before orchestrator approval."
- ❌ Omitted entirely.

**Rule D4 — State exclusion boundaries for near-neighbors.** If another skill covers adjacent territory, state what this skill does NOT do.
- ✅ "DO NOT USE FOR: multi-task orchestration; does not update tracking files."
- ❌ No exclusion when a near-neighbor exists.

**Rule D5 — Include domain markers.** Name the technology, platform, artifact type, or tool that scopes the skill.
- ✅ "C# Roslyn and SonarQube issues"; "tracking files in `.ai/`"
- ❌ "Processes project files and returns results" — generic terms like *code, files, project, task, output, data, system* are not domain markers.

Length target: 1–3 sentences. Never a bare keyword list. Never a restatement of the skill name.

---

## 5. Design Principles

These principles apply across all skills and are not superseded by any individual section guidance above.

### Skill Isolation

**[GSR-01/17]** Skills must declare required upstream artifacts as explicit Inputs entries rather than naming another skill. Skills must not reference another skill by name or path in workflow steps, frontmatter descriptions, scope boundaries, or exclusion text.

The orchestrator is the exclusive owner of cross-skill wiring.

**Signs of failure**: a step that says "invoke skill-x"; a description that redirects to another skill; a skill that depends on a sibling skill instead of an input artifact.

### Gate Before Acting

**[GSR-02]** Every irreversible or high-risk action must be preceded by an explicit gate. A gate is a condition that must be true, or a confirmation that must be obtained, before execution continues.

Use `⛔ **STOP**` at the end of a step when an intermediate boundary is mandatory but not naturally self-blocking. Do not add a STOP after a step that already ends with a user interaction or a destructive-action gate.

**Signs of failure**: a skill that runs all phases sequentially with no checkpoints; a write gate that is implied but not explicit.

### Blocking Gate Protocol

**[GSR-21]** When a skill includes a blocking gate, it must follow this protocol:
1. State `BLOCKED` or `CLEAR` explicitly.
2. List specific blocking item IDs and one-line summaries.
3. State whether the handoff can proceed or is stopped, and name the next skill or action when approved.
4. Include the blocking notification section even when there are zero blockers.

**Signs of failure**: critical issues appear in the body but no explicit blocking status is given; downstream handoff proceeds silently despite blockers.

### One Role Per Skill

**[GSR-08]** A skill should do one thing. If a skill is invoked in two different contexts, identify both roles at the top of the file and route execution to the appropriate procedure based on invocation context.

Do not create two near-identical sibling skills to cover the two roles. Keep shared rules co-located.

### Idempotency and Resumability

**[GSR-09/10]** For multi-step skills, progress must be externalized so execution can resume after interruption. Use checkbox task lists in persistent tracking files as the authoritative task state.

A skill must also behave correctly whether it is invoked for the first time or against partially existing state. Before creating files or taking actions, inspect current state and branch accordingly:
- If a tracking file exists with incomplete tasks → resume from where it left off.
- If an output file already exists → read and update rather than recreate.
- If a resource already exists → detect and skip or update rather than duplicate.

Document all three branches explicitly: first run, resume, and already complete.

**Signs of failure**: all state exists only in the context window; a skill that always recreates files; a skill that restarts the workflow because one step was interrupted.

### Runtime Failure Documentation

**[GSR-11]** Every skill has expected runtime conditions such as authentication expiry, empty results, missing files, unavailable tools, or API errors. Document the response to each predictable failure.

Use `> **If {situation}**: {specific action}` callouts at the step where each failure can occur. "Handle the error gracefully" is not an acceptable response.

### Reference File Reading

**[GSR-15]** When a skill reads any catalogue, ruleset, knowledge base, or other lookup file, the step that performs the read must explicitly require reading to the end of the file — using successive `read_file` calls until the response is shorter than the page size.

Canonical pattern:
1. Read from line 1 with a generous range.
2. If the response contains a full page of content, advance `startLine` and read again.
3. Repeat until the response is shorter than the page size.

Apply this to lookup sources such as catalogues, rule sets, mapping tables, and knowledge bases.

**Signs of failure**: a single `read_file` call on a catalogue; a knowledge lookup that misses entries past the first page.

### Context Loading

**[GSR-14/20]** A skill must not require its caller to have pre-loaded files or state on its behalf. Any file or configuration a skill needs must be loaded by the skill itself in its first step.

Load only the minimum context required from each artifact. Use progressive disclosure: load structure first, then the specific sections needed for the current step. Do not exceed 60–70% of the effective context window with loaded content.

**Signs of failure**: a context section that says the caller must preload files; loading all constitution sub-files when one is relevant; loading an entire repo summary for a narrow task.

### External Knowledge Files

**[GSR-13]** A skill file should be a workflow, not a reference manual. Put deep domain knowledge in co-deployed files in `ai/plugins/skf/knowledge/` and reference them from the skill.

A non-generator skill should stay in the 80–250 line range. A skill longer than 300 lines is often carrying reference material that belongs elsewhere.

### Clean-Run vs. Update

**[GSR-19]** The correct behavior on re-run depends on artifact role:

- For `output-type: report`: delete any prior output file, create a new empty file, generate fresh content without reusing prior report content.
- For `output-type: artifact`: read the existing artifact first and update it in place; never delete or recreate from scratch; preserve progress and history.

---

## 6. Language Conventions

Skills are guidance documents, not functions.

**Use "consult" only for reading guidance**, not for cross-skill routing:
- ✅ "Consult `skill-design-guide.md` for the reusable patterns"
- ❌ "Call the user-input skill"; "Invoke the loop skill"

**Avoid input/output/return language** when describing how skills interact:
- ✅ "The skill produces a structured result in this format: ..."
- ✅ "After this skill completes, the calling agent uses the result"
- ❌ "Returns a value to the caller"; "Takes a parameter as input"

**Avoid code syntax in prose.** Variable syntax, boolean expressions, and language constructs belong inside fenced code blocks only. Tool names and function names in backticks are acceptable; variable names and expressions are not.

**Bold named artifacts** when a step constructs a data structure that is referenced later by name. Use the name consistently across all uses.

---

## 7. Reusable Patterns

Embed these patterns directly in the skill body where needed. Do not reference them as external dependencies.

### Bounded Loop Pattern

Use this pattern anywhere a skill must repeat a phase until a condition is met:

```
### Step N — [Phase name] (loop)

**Exit condition**: [state that ends the loop]
**Max iterations**: [N, typically 3–5]

1. [Perform the iteration body]
2. Evaluate the exit condition.
   - If met → proceed to Step N+1.
   - If not met and iterations remain → repeat from 1.
   - If max iterations reached → ⛔ STOP. Report the situation and call `vscode_askQuestions` directly:
     ```json
     {
       "header": "loop_stall",
       "question": "Could not reach exit condition after [N] attempts. How to proceed?",
       "options": [{ "label": "Try again" }, { "label": "Abort" }],
       "allowFreeformInput": true
     }
     ```
```

Rules:
- Each iteration must make observable progress toward the exit condition.
- Carry forward context from the previous iteration.
- Never loop silently past the max.

### Interactive Skill Callout Pattern

Use this callout at the beginning of Section 3 (Behavioral Anchors) → Operational Anchors if the skill calls `vscode_askQuestions` to collect user decisions:

```markdown
> **Interactive skill** This skill calls `vscode_askQuestions` to collect decisions and cannot interact with user when dispatched as a stateless subagent.
```

**When to use**: Any skill that requires user input via `vscode_askQuestions` and thus depends on an interactive runtime. This warning alerts orchestrators and calling contexts that the skill cannot be used in headless, batch, or subagent-only deployments.

**Placement**: Add this callout in the Operational Anchors subsection if the skill makes ANY call to `vscode_askQuestions` in its workflow. Do not add it if all user input is collected via stdin or file-based configuration.

---

## 8. Authoring Workflow

Follow this workflow when creating a new skill:

**Step 1 — Define scope and constraints.** Before writing anything, answer: What exactly does this skill do? What must NOT be done? What are the highest-risk failure modes? Which skill handles the adjacent task (for the scope boundary)?

**Step 2 — Draft the workflow.** Write out the step-by-step procedure: all inputs, every step and branch, all outputs, the done condition.

**Step 3 — Design the output format.** Define the exact output shape before writing the full skill. What structure will the skill produce? Show it as a template.

**Step 4 — Write Section 4 (Workflow) first.** Write the full detailed workflow section. This is your design specification.

**Step 5 — Extract Sections 1–3 from the workflow.** Write:
- **Section 1 — Identity**: One-paragraph summary + scope boundary
- **Section 2 — Constraints**: Extract prohibitions from the workflow; phrase as NEVER/ALWAYS rules with WHY
- **Section 3 — Behavioral anchors**: Add Environment Preflight subsection (devcontainer and host branches); extract Operational Anchors including guidance on prioritization, ambiguity handling, and idempotency

**Step 6 — Write Sections 5–8:**
- **Section 5 — Tools**: List tools used in workflow steps with "when and how" guidance
- **Section 6 — Output format**: Show the exact template from Step 3
- **Section 7 — Examples**: 2–3 representative examples + 1 counter-example
- **Section 8 — Reminders**: Repeat the 2–4 most critical constraints from Section 2

**Step 7 — Add frontmatter.** Add the full frontmatter block with all standard fields, using the disambiguation rules for the `description` field.

---

## 9. Common Authoring Pitfalls

### Pitfall 1: Mixing Constraints with Guidance

**Problem**: Putting positive instructions ("Always check the build status") in Section 2.

**Solution**: Constraints are PROHIBITIONS only. "Never skip the build status" goes in constraints. "Always check the build status before reporting" is a behavioral anchor.

### Pitfall 2: Burying Critical Rules in Workflow Steps

**Problem**: Writing "Do not create iteration folders" inside a workflow step.

**Solution**: Extract as a constraint in Section 2. Reference it from the workflow; do not state it there.

### Pitfall 3: Oversummarizing the Workflow

**Problem**: Condensing a 10-step process into 4 summary paragraphs to save space.

**Solution**: Preserve every step verbatim. If the workflow is complex, that may signal the skill is doing too much — but do NOT summarize. Consider splitting into multiple skills instead.

### Pitfall 4: Forgetting the Scope Boundary

**Problem**: An identity section that doesn't explain what the skill does NOT do.

**Solution**: Every skill must state: "This skill does NOT [X]. For [X], use [sibling-skill-slug]." The boundary is as important as the purpose.

### Pitfall 5: Vague Output Template

**Problem**: "Return a structured summary of the changes made."

**Solution**: Show a concrete template with field names, order, and types.

### Pitfall 6: Examples That Don't Show the Output

**Problem**: "Example 1: Create a file. Expected behavior: Confirm it was created."

**Solution**: Show both the input and the exact output the skill produces.

---

## 10. Validation — Check/Fix Catalogue

The sections below define every check-and-fix rule used when evaluating and refining skills. Each entry has two sides:

- **Check** — what to inspect to determine pass/fail.
- **Fix** — what to change to remediate a violation.

### Scoring Rubric

Every **Check** is scored with one of three statuses:

| Status | Meaning |
|--------|---------|
| ✅ | The criterion is fully met — no action needed. |
| ⚠️ | The criterion is partially met or ambiguous — a minor fix is needed. |
| ❌ | The criterion is not met — a fix is required before the skill is compliant. |

Each entry's **Check** section specifies which status to assign for each condition it describes. When a check condition passes, assign ✅.

---

### Rule: Frontmatter name and description meaningful

**Check**: The YAML frontmatter must contain an `id` field that is a lowercase hyphenated slug matching the skill's filename, and a `description` field that follows all five disambiguation rules (D1–D5) from [the Frontmatter Requirements section above](#4-frontmatter-requirements).

**Prerequisite**: Before evaluating D-rules, list every skill slug in the workspace together with its one-line description. Use this inventory to identify near-neighbors for D4.

**Severity aggregation**: The overall status equals the **worst** individual D-rule status (e.g. D1=✅, D2=⚠️, D3=❌ → overall ❌).

- **D1 — Action + object first**: Must start with a verb and name the concrete action and target. Flag ❌ if it opens with the skill name, a noun phrase, or a blocklisted generic verb (*Handles, Manages, Processes, Provides, Supports, Facilitates, Enables, Maintains, Deals with, Takes care of, Is responsible for*).
- **D2 — Output named**: Must state what artifact, result, or state change the skill produces. Flag ⚠️ if output is implied but not named. Flag ❌ if no output is discernible.
- **D3 — Trigger condition**: Must contain a `USE FOR:`, `Consult this skill when:`, or equivalent clause. Flag ⚠️ if only weakly implied. Flag ❌ if absent.
- **D4 — Exclusion boundary**: If any skill covers adjacent territory, the description must include a `DO NOT USE FOR:` clause redirecting to the sibling. Flag ⚠️ if a near-neighbor exists and no exclusion is stated. Flag ✅ if no near-neighbors exist.
- **D5 — Domain markers**: Must include at least one technology, platform, artifact type, or tool name. Generic terms (*code, files, project, task, output, data, system, items, resources, results, workflow, process*) do not count. Flag ⚠️ if no domain marker remains after excluding blocklisted terms.

Additionally flag ❌ if either field is absent, if `description` is a conversion artifact, a restatement of the skill name, or a bare keyword list.

**Fix**: Correct the `id` slug if wrong. Rewrite the `description` following this template:

```
<Verb> <object/target>, <producing what output>. USE FOR: <trigger condition>. DO NOT USE FOR: <exclusion, with sibling redirect if applicable>.
```

Include at least one domain marker. Keep to 1–3 sentences. Omit the DO NOT USE FOR clause if D4 is ✅ (no near-neighbors).

---

### Rule: Steps are numbered

**Check**: Every procedural sequence must use `## Step N — Title` headings inside `<workflow>`. Flag ❌ if actions are described as unnumbered bullet lists or prose paragraphs without a step heading.

**Fix**: Convert unnumbered bullet lists or prose paragraphs that describe a sequence of actions into `## Step N — Title` headings with numbered or bulleted sub-items. Preserve content; only restructure.

---

### Rule: Inputs collected before execution begins

**Check**: The skill must not perform any action before all required inputs are confirmed. Flag ❌ if the first executable step acts on an undeclared input, or if clarifying questions appear mid-workflow rather than upfront.

**Fix**: Move all input collection to the first step. Call `vscode_askQuestions` directly to batch all unknown fields in a single call. Do not use plain-text question lists.

---

### Rule: Output has a defined structure

**Check**: If the skill produces a result that will be read by a user or another skill, that result must be defined with an explicit template — field names, order, and allowed values. Flag ❌ if the status fields are described only in prose without a structured table or fenced template block.

**Fix**: Add a standard field table (status, skill_id, output_path, summary) to `<output_format>`. For operation-specific output, add named fenced code blocks showing the exact output shape with placeholder values. A prose description alone is not sufficient.

---

### Rule: Done condition stated

**Check**: The skill must contain an explicit statement of when it is complete. Flag ⚠️ if the last step ends with "generate the output" with no completion criterion. Flag ❌ if there is no completion statement at all.

**Fix**: Add a completion statement to the last step: "The skill is complete when `{file}` exists on disk and the confirmation has been shown to the user." Also add measurable done conditions to the `## Done conditions` subsection in the workflow.

---

### Rule: Rules section with prohibitions

**Check**: The skill must have a `## Rules` section (inside `<reminders>`) with at least two to three concrete prohibitions. At minimum one must address scope overreach. Flag ❌ if the section is absent or contains only positive instructions.

**Fix**: Add a `## Rules` section inside `<reminders>`. Include at least the scope-overreach prohibition. Each rule must describe a concrete action to avoid.

---

### Rule: Runtime failures documented

**Check**: For each foreseeable failure mode — missing file, auth expiry, empty result, API error, unavailable tool — the skill must have an inline `> **If {situation}**: {specific action}` callout at the step where that failure can occur. Flag ⚠️ if at least one foreseeable failure has no documented response.

**Fix**: At each step where a failure can occur, add a `> **If {situation}**: {specific action}` callout. The action must name the exact command to retry, the message to show, or the decision to make. "Handle the error gracefully" is not acceptable.

---

### Rule: Idempotency and resume check

**Check**: If the skill creates files, work items, or other resources, it must check for prior existence before acting. Flag ❌ if there is no state-detection branch covering: not yet created → proceed; partially complete → resume; already complete → report and stop.

**Fix**: Add a state-detection block to the initialization or first step with explicit branches for all three states. If the skill creates no persistent resources, mark as ✅ (not applicable).

---

### Rule: Sibling skills referenced by name

**Check**: Every skill that is consulted must be named by its exact id in bold (e.g. **orch-orchestration-plan**). Flag ❌ if any reference uses "the appropriate skill", "a sub-skill", or similar vague terms.

**Fix**: Replace vague references with the exact skill id in bold. If the correct skill id is unknown, use `**[SKILL ID NEEDED]**` rather than a vague reference.

---

### Rule: No code syntax in prose

**Check**: Flag ❌ if the skill body contains scripting variable syntax (e.g. `$var`), expressions (e.g. `$x -ne 0`), or literal language constructs outside a fenced code block. Tool names and function names in backticks are acceptable; variable names and expressions are not.

**Fix**: Rewrite the offending phrase in plain language. Move implementation detail into the nearest fenced code block.

---

### Rule: Bold named artifacts

**Check**: Flag ⚠️ if the skill constructs a named data structure in one step and references it by name in a later step, but does not bold the artifact name at either point. Does not apply to field values, transient variables, or terms that appear only once.

**Fix**: Bold the artifact name on first use (where it is built) and at every subsequent reference. Use a consistent noun phrase across all uses.

---

### Rule: No unresolved platform-specific variable syntax

**Check**: Flag ❌ if the skill body contains `${input:foo}`, `${workspaceFolder}`, or similar VS Code task/prompt-file variables outside a clearly labelled boilerplate template block.

**Fix**: Replace with plain prose placeholders: `<foo>` or `<description of value>`. Variables inside a boilerplate template block may remain if they are explained as substitution points.

---

### Rule: Consult language used throughout

**Check**: Flag ❌ if the skill body uses "call the X skill", "invoke the X skill", "use the X skill", "X returns Y", or "pass Y to X" to describe inter-skill interaction.

**Fix**: Replace "call/invoke/use [skill]" with "consult the **[skill]** skill". Replace "[skill] returns Y" with "the skill produces Y". Replace "pass Y to [skill]" with "provide Y in the conversation context before consulting [skill]".

---

### Rule: Size within bounds

**Check**: Flag ⚠️ if the skill is under 40 lines (likely a stub). Flag ⚠️ if it exceeds 300 lines and is not a generator skill with embedded boilerplate templates.

**Fix**: For stubs — expand the workflow with concrete steps, an output template, and a Rules section. For oversized skills — identify content that belongs in a co-deployed reference file under `ai/plugins/skf/knowledge/` and move it there.

---

### Rule: Reference files read in full

**Check**: If a skill reads any catalogue, ruleset, knowledge base, or other lookup file, the step that performs the read must explicitly require reading to the end — using successive `read_file` calls until the response is shorter than the page size. Flag ❌ if the skill reads such a file with a single `read_file` call and no continuation instruction. Flag ❌ if the `## Rules` section does not prohibit acting on a partial read.

**Fix**: In the step that reads the lookup file, replace the single `read_file` instruction with the multi-pass pattern. Add to `## Rules`: "Never act on a partially read catalogue, ruleset, or knowledge-base file — read to end of file before evaluating."

---

### Rule: Structural tag compliance detection uses line-start anchor

**Check**: Wherever a skill or script checks whether a file contains a structural XML section tag (e.g., `<constraints>`, `<workflow>`, `<tools>`), verify that the detection command uses a line-start anchor. Flag ❌ if `grep -rl "<tag>"` or equivalent is used without a `^` anchor — this matches inline prose references and produces false positives. Flag ⚠️ if `grep -Pn "^<tag>"` is used — this may be unreliable in some environments.

**Fix**: Replace any plain `grep -rl "<tag>"` structural detection with:
```bash
awk '/^<constraints>/{found=1} END{exit !found}' "$f"
```
Substitute the target tag name as appropriate.

---

### Rule: Sub-agent prompt deduplication

**Check**: When a skill dispatches multiple sub-agents for batch transformations, check whether identical rule blocks or reference content (>10 lines) are copy-pasted inline into more than two sub-agent prompts. Flag ⚠️ if the same content block appears in more than two sub-agent prompts within the same skill.

**Fix**: Extract the shared content into a named knowledge file in `ai/plugins/skf/knowledge/` and instruct sub-agents to load it via `read_file` at the start of their prompt. Remove the inline copy from each sub-agent prompt.

---

### Rule: U-shape section ordering

**Check**: The skill body must contain all 8 U-shape sections in the correct order: (1) identity, (2) constraints, (3) behavioral_anchors, (4) workflow, (5) tools, (6) output_format, (7) examples, (8) reminders. Detect sections by their XML tags and the identity block at the top. Flag ❌ if fewer than 6 sections are present or the ordering has more than one transposition. Flag ⚠️ if 6–7 sections are present or the ordering has exactly one transposition.

**Fix**: Reorder sections to match the canonical sequence: identity → `<constraints>` → `<behavioral_anchors>` → `<workflow>` → `<tools>` → `<output_format>` → `<examples>` → `<reminders>`. Move sections as units; do not alter content within each section.

---

### Rule: XML section boundaries

**Check**: The skill body must use XML tags for section demarcation. Required tags: `<constraints>`, `<behavioral_anchors>`, `<workflow>`, `<tools>`, `<output_format>`, `<examples>`, `<reminders>`. Flag ❌ if fewer than 4 of these tags are present and the skill relies solely on markdown headers. Flag ⚠️ if 4–6 tags are present (at least one missing).

**Fix**: Wrap each section in its corresponding XML tags. Each opening tag appears on its own line immediately before the section content; the closing tag appears on its own line immediately after. Do not rename or abbreviate the standard tag names.

---

### Rule: Behavioral anchors present

**Check**: The skill must contain a `<behavioral_anchors>` section with: (a) an Environment Preflight subsection with devcontainer and host branches; (b) an Operational Anchors subsection with an anti-drift clause and a self-checking instruction. Flag ❌ if the section is absent or missing any of the three required components. Flag ⚠️ if present but any component is incomplete or unclear.

**Fix**: Add a `<behavioral_anchors>` section positioned after `<constraints>` and before `<workflow>`. Structure it with two subsections:

```markdown
## Environment Preflight
If `env` is `devcontainer`: read `ai/plugins/skf/knowledge/devcontainer-guidelines.md` fully (follow multi-pass read if needed) and apply all devcontainer rules before proceeding to Step 1.
If `env` is `host`: no additional action required.

## Operational Anchors
- Before producing output, verify your output complies with all rules in <constraints> above.
- Implement EXACTLY and ONLY what the skill instructs — no extra features, no unrequested refactors.
- [Additional operational anchors as appropriate]
```

---

### Rule: Examples section present

**Check**: The skill must contain an `<examples>` section with at least 2 complete end-to-end demonstrations AND at least 1 counter-example (marked with `type="counter"` or equivalent). Each example must show: inputs → key decision → output. Flag ❌ if absent or contains only 1 example. Flag ⚠️ if 2+ examples present but no counter-example.

**Fix**: Add an `<examples>` section after `<output_format>` and before `<reminders>`. Include 2 positive demonstrations and 1 counter-example. Each example must be concrete — use realistic inputs, not placeholders.

---

### Rule: Critical reminders at end

**Check**: The skill must contain a `<reminders>` section as the last section of the body. It must restate at least 2 of the constraints from `<constraints>` — no new constraints may be introduced. Flag ❌ if the section is absent. Flag ⚠️ if present but restates only 1 constraint, or introduces constraints not in `<constraints>`.

**Fix**: Add a `<reminders>` section as the last element of the skill body. Copy the 2–3 most critical constraints from `<constraints>` verbatim or as close paraphrases. Do not introduce new rules.

---

### Rule: Constraint rationale present

**Check**: Every non-trivial constraint in `<constraints>` must include a WHY explanation — inline ("WHY: …") or as a parenthetical reason. Trivial constraints (e.g. "Read files before editing") are exempt. Flag ⚠️ if 1–2 non-trivial constraints lack WHY. Flag ❌ if no constraints include WHY rationale.

**Fix**: For each constraint lacking WHY rationale, append an inline explanation: `WHY: {one sentence explaining the risk or reason this constraint exists}`. One sentence per constraint is sufficient.

---

### Rule: Bidirectional constraints

**Check**: Safety constraints (governing scope, safety, or irreversible actions) must state both what IS allowed AND what is forbidden — not only one direction. Flag ❌ if the `<constraints>` block contains safety rules that state only one direction. Flag ⚠️ if at least one safety rule is unidirectional while others are bidirectional.

**Fix**: For each unidirectional safety constraint, add the complementary statement: "Use [tool] ONLY for [purpose] — NEVER for [forbidden action]." If the constraint only permits, add the boundary: "Prefer [action] — do not [forbidden action]."

---

### Rule: Tag validation

**Check**: Every tag in the skill's frontmatter `tags:` list must exist in the canonical vocabulary in `ai/plugins/skf/knowledge/skill-tags.md`. Flag ❌ if any tag is not found in that vocabulary.

**Fix**: Replace non-canonical tags with the closest canonical equivalent found in `skill-tags.md`. Do not invent new tags.

---

### Rule: Tag count

**Check**: The `tags:` list must contain 3–4 tags. Flag ⚠️ if the count is outside this range (fewer than 3 or more than 4).

**Fix**: Add tags from `skill-tags.md` to reach 3, or remove the least specific tag to reduce to 4.

---

### Rule: Primary category tag first

**Check**: The first tag in `tags:` must be one of the primary category tags: `governance`, `implementation`, `meta`, `planning`, `quality`, `specification`, or `utility`. Flag ❌ if the first tag is not a primary category tag.

**Fix**: Reorder so that the appropriate primary category tag appears first. If no primary category tag is present, add the correct one and remove a secondary tag if needed to stay within the 3–4 limit.

---

## 11. Quick Checklist — Before Publishing a Skill

- [ ] **Frontmatter** contains all standard fields: `id`, `recommended-tier`, `version`, `description`, `anti-scope`, `tags`, `inputs`, `outputs`, `dispatch-variant`
- [ ] **`description`** follows all 5 D-rules (action verb, output named, trigger, exclusion, domain marker)
- [ ] **Section 1 — Identity**: one paragraph; scope boundary stated; sibling skill slug referenced
- [ ] **Section 2 — Constraints**: 3–6 NEVER/ALWAYS rules, each non-trivial rule has `— WHY:` rationale; bidirectional for safety rules
- [ ] **Section 3 — Behavioral anchors**: Environment Preflight subsection present; Operational Anchors subsection with compliance self-check and anti-drift clause; 3–5 operational anchor bullets
- [ ] **Section 4 — Workflow**: `## Preflight` and `## Done conditions` subsections present; steps numbered; branches marked; done condition in last step is measurable and unambiguous
- [ ] **Section 5 — Tools**: all tools used in workflow are listed; all listed tools are actually used
- [ ] **Section 6 — Output format**: standard field table present with all enum values; operation-specific output in named fenced blocks
- [ ] **Section 7 — Examples**: at least 2 positive demonstrations + 1 counter-example (`type="counter"`); both show Input and Expected behavior
- [ ] **Section 8 — Reminders**: 2–4 critical constraints repeated from Section 2; imperative phrasing; no new constraints introduced
- [ ] **No sibling skill referenced by path or vague term** — use exact skill id in bold
- [ ] **No code syntax in prose** — variable syntax and expressions are inside fenced code blocks
- [ ] **No unresolved `${variable}` syntax** outside boilerplate template blocks
- [ ] **Language conventions followed** — "consult" for guidance reading; no "call/invoke/return" for skill interaction
- [ ] **Skill length appropriate** — not a stub (<40 lines); not carrying reference material (>300 lines unless generator)
- [ ] **All predictable runtime failures** have documented responses at the step where they occur
- [ ] **Reference files** (catalogues, rulesets, knowledge bases) are read with multi-pass pattern to end of file
