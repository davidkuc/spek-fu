---
description: "Quickstart template — a runnable operator guide for a feature: setup, run, verify"
---

<!--
================================================================================
AUTHORING RULES — read before writing. Delete every HTML comment from the final file.
================================================================================

A quickstart is a RUNNABLE DOCUMENT, not a summary. The test it must pass:

  A competent engineer who has never seen this feature can follow it top to bottom,
  typing only what is written, and reach a working system plus a verified verdict —
  without opening the spec, the plan, the contracts, or the source.

Any sentence that sends the reader elsewhere to find a name, a path, a value, or a
decision is a defect. The ten rules below are how that test is passed. They are
BINDING, not advisory.

R1 — NAME THE ARTIFACT. Every instruction resolves to something typed or clicked.
     Never "configure the client", "enable the capability", "set the limits".
     Always: the exact file path, the exact config key, the exact CLI flag, the exact
     env var, the exact field name, the exact button label.
     ✗ "Decide which capabilities to enable."
     ✓ "`app serve --enable-mutating-operations` — without the flag, `POST /v1/ops/*`
        returns 412 naming the flag."

R2 — GROUND EVERY NAME IN THE REPOSITORY. Before writing a flag, key, path, endpoint,
     or field, read it out of source, contracts, or an existing sibling quickstart.
     Never invent one. If the name does not exist yet because this feature creates it,
     write the name AND say which task introduces it and in which file.
     If it cannot be grounded or derived, emit `[NEEDS CLARIFICATION: <question>]` —
     never a plausible-looking guess.

R3 — CONCRETE VALUES, NOT PLACEHOLDERS. Use the feature's real defaults (real port,
     real default seconds, real directory). Where a value is genuinely per-user (a
     token, a generated id), show the command that produces it. Where a value is
     illustrative, say so in the same line.

R4 — COPY-PASTEABLE COMMANDS. Declare the shell convention once, up front, and stay in
     it. Give a second shell's equivalent only where the two differ meaningfully. Setup
     steps assign named variables that later steps reuse, so the reader never re-types
     a path. Prefer a real verification command over prose ("-> True").

R5 — CHOICES BECOME TABLES. Any "it depends" turns into a table whose columns are
     *what you want* → *the exact thing you type* → *what happens without it*.
     A refusal, error code, or exit code is part of the table, not a footnote.

R6 — EVERY VERIFY STEP IS COMMAND + PASS CONDITION. A verification step that states an
     expectation without a command to produce it is not verification. Where a plausible
     wrong outcome exists, state what FAIL looks like and what it means. Assert on
     fields and observable output, never on "it seems to work".

R7 — TAG WHAT CANNOT BE AUTOMATED. Mark manual-only checks `[MANUAL]` and say in one
     clause why an automated test cannot honestly carry the claim. Platform-gated checks
     must say they are to be REPORTED AS SKIPPED elsewhere, never silently passed.

R8 — ONE CLAUSE OF WHY, WHERE IT IS LOAD-BEARING. When a step guards against a real
     failure, say which failure in the same sentence. No filler rationale, no restating
     the command in words.

R9 — FLAG GAPS HONESTLY, INLINE. If a step depends on something the feature's own
     artifacts do not yet cover (a task that does not exist, a schema that rejects the
     key, a spawn call missing an argument), say so at the point of use and give the
     workaround. Never assert a path works because it ought to.

R10 — TRACE RULES TO DECISIONS. Where a step exists because of a requirement or
     decision, cite it inline (FR-0xx, D-0xx, SC-0xx). The reader must be able to get
     from a surprising instruction to the reason for it in one hop.

STYLE
- Tables for anything enumerable; prose only for reasoning that a table would flatten.
- Imperative voice, short paragraphs, no marketing tone, no praise of the design.
- A step that writes to or mutates a shared/committed fixture MUST instead operate on a
  scratch copy created in Setup — never on the fixture in place.
- Sections may be dropped when a feature genuinely has no surface for them (a
  library feature has no "Key Endpoints"). Never drop Verify.

SELF-CHECK BEFORE WRITING THE FILE
1. Search the draft for: "configure", "set up", "enable", "decide", "as needed",
   "appropriate", "the relevant", "somehow". Each hit must resolve to a named artifact
   in the same sentence or be rewritten.
2. Every fenced command block: could it be pasted as-is after the preceding steps?
3. Every Verify step: does it have both a command and a pass condition?
4. Every flag/key/path/field: was it read from the repo, or is it marked as introduced
   by a named task, or is it a [NEEDS CLARIFICATION] marker?
5. Zero unresolved `[TODO]`, `[TBD]`, or unreplaced bracket placeholders.
================================================================================
-->

# Quickstart: [FEATURE NAME] ([FEATURE NUMBER])

## Feature Summary

[One or two paragraphs: what the feature gives the user, in plain language, naming the
concrete surfaces it adds. Then the scope boundaries a reader will otherwise assume
wrongly — what does NOT change, and what is off by default and why.]

**Conventions in this document.** [Shell and platform used by the examples. The variable
names Setup assigns and later steps reuse. Any value that is fixed (a default port) versus
per-run (a generated token).]

## Prerequisites

<!-- R1/R3: a table, not a wish list. Every row says how to satisfy it and why it exists. -->

| Requirement | How to satisfy it | Why |
|---|---|---|
| [Runtime + version] | `[exact check command]` | [What breaks without it] |
| [Dependency / extra] | [Setup step reference] | [What it carries] |
| [Seed data / fixture] | [Setup step reference] | [Which operations need it] |
| [Credential / consent] | `[exact command]` | [The exact failure without it] |

[One line on network/egress posture if the feature touches it.]

## Setup

<!-- Numbered, named steps. Each ends with a command whose output the reader can check. -->

### 1. [Install / provision]

```[shell]
[exact command]
```

[Anything this changes that another owner needs to know — raised dependency floors, new
compiled artifacts, new files on disk.]

Confirm it landed:

```[shell]
[exact verification command]   # -> [expected output]
```

### 2. [Configure — name the store, the keys, and the exact commands]

[Where configuration actually lives — the file or registry path — and the command that
reads and writes it. Not "configure the feature".]

**[Default / no-cost path]:**

```[shell]
[exact config command]
[exact list/get command]
```

**[Real / production path]:** [what additional things are required, each as a command]

```[shell]
[exact config command]
[exact consent/credential command]
```

[The exact failure produced by skipping one of these, quoted as the reader will see it.]

### 3. [Choose behaviour — the table that replaces "decide which…"]

| To do this | Use | Without it you get |
|---|---|---|
| [Capability / mode / flag] | `[exact flag or command]` | `[exact status code + message]` |
| [Capability / mode / flag] | `[exact flag or command]` | [exact observable failure] |
| [Always-available behaviour] | *(nothing)* | — |

[Where the enabled set is observable — descriptor, health endpoint, log line.]

[R9: if any path here is not yet wired, state the gap and the workaround at this point.]

### 4. Optional — [tuning knobs for local experiments]

| Config key | Default | What it bounds | Useful local value |
|---|---|---|---|
| `[key]` | `[value]` | [one clause] | `[value]` |

```[shell]
[exact set command]
[exact get command]
```

> **Implementation note, not a user step.** [Which names are already fixed by a decision,
> which are introduced by which task and file, and any schema or validation that must be
> extended for the commands above to work at all.]

## Run

### 1. [Start the system]

```[shell]
[exact startup command, including credential provisioning]
```

[The exact ready output, quoted. The exact artifacts written and their full paths. The
exact refusal behaviour on the common conflict (already running, port taken) and why it
fails closed rather than falling back.]

### 2. [Primary surface — e.g. the UI]

```[shell]
[exact launch command]
```

1. [Exact UI action, with the exact control label.]
2. [Exact next action, and the state that gates it.]
3. [What is disabled while busy, and what the reason text says.]
4. [What happens on success.]

### 3. [Secondary surface — e.g. a script]

<!-- R4: discovery first, hard-coding never. Show the safe way, and name the unsafe way
     that is being avoided. -->

```[shell]
[discovery block: locate the endpoint/credential from its recorded location]
[liveness or validity check, with the rule it follows]
$[BASE] = [...]
$[AUTH] = [...]
```

```[shell]
[start the operation]
[poll to a terminal state, printing the fields that matter]
[read the terminal fields]
```

[Second-shell / other-language equivalent, only if it differs meaningfully.]

### 4. [Tertiary surface — e.g. an agent or external client]

[The exact configuration artifact, as a fenced block the reader can paste:]

```json
[exact config file content]
```

[Which fields are stable across restarts and which rotate, so the reader knows what to
re-do each session. What is deliberately not exposed here and where it lives instead.]

### Key Endpoints

| Method | Path | Purpose |
|---|---|---|
| [VERB] | `[path]` | [one clause; note auth exceptions and parameters inline] |

[One short paragraph only if two surfaces have deliberately different call shapes — say
what differs and what is identical underneath.]

## Verify

<!-- R6: every step is command + pass condition. R7: tag the manual ones. -->

Each check below is a command plus the observation that makes it pass. Run them
[against what, with which variables set].

### 1. [The property being verified, stated as a claim]

```[shell]
[exact command]
```

**Pass**: [the exact observable]. **Fail**: [the plausible wrong outcome and what it means].

### 2. [Next property]

```[shell]
[exact command]
```

**Pass**: [exact observable].

### N. [Refusals are explicit and distinguishable]

<!-- Cross-product tables beat prose for refusal checks. -->

| Provoke it with | Expect |
|---|---|
| `[exact input]` | `[exact code + payload field]` |

### N+1. [Property that cannot be automated] **[MANUAL]**

```[shell]
[exact command sequence, including the setup that makes the check meaningful]
```

**Pass**: [exact observable]. [Why an automated test cannot honestly carry this claim.]

> **[MANUAL] summary.** [Which steps are manual and the one-clause reason each cannot be
> automated into an honest pass. Which are platform-gated and must be reported as skipped
> rather than silently passing elsewhere.]

## Troubleshooting

<!-- Failure modes the steps above actually produce, in the reader's own words. -->

| Symptom | Cause | Fix |
|---|---|---|
| `[exact error text or code]` | [the real cause] | `[exact command or step reference]` |
