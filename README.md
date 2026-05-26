# 🚀 Spek-Fu

> **A self-learning agent orchestration system that grows with your project.**

Spek-Fu is an **AI agentic development framework** built around a general-purpose orchestrator that:
- Decomposes requests into **subagent waves**
- Routes each wave through a **tiered agent pool**
- Keeps **humans in control during specification** while AI drives implementation
- Progressively distills operational experience into **reusable behavioral patterns**
- Compounds gained knowledge with **every session**

## Framework Architecture

### Orchestration System

**`@skf-general-orchestrator`** is the top-level coordinator:

1. **Receives a request** → traverses the index chain from `skf-root-index.json` to locate applicable skills, knowledge, and patterns
2. **Decomposes the work** → breaks down into ordered waves
3. **Dispatches each wave** → issues clean-slate subagent calls
4. **Routes subagents** → selects appropriate tier (`fast-agent`, `standard-agent`, `large-context-agent`) based on skill's `recommended-tier` and complexity
5. **Delegates or stops** → orchestrator never executes tasks directly


### Compound Engineering

Two complementary databases feed the orchestration cycle:

| Database | Purpose | Example |
|----------|---------|----------|
| **Knowledge** `spek-fu/ai/plugins/skf/knowledge/` | Operation-specific lessons (project-scoped) | "Always read devcontainer-guidelines.md before writing" |
| **Patterns** `spek-fu/ai/plugins/skf/patterns/` | Reusable behavioral strategies (PT0xx files) | PT007: Just-in-Time Retrieval, PT023: Parallelization |

**Key distinction:** Lessons are specific & operational (stay local) • Patterns are general & structural (travel across projects)


### Self-Learning Loop

1. **Lessons accumulate** in `knowledge-database.md` through normal operation.
2. **Threshold check**: When the lesson count reaches the configured threshold (`knowledgeDistillationThreshold` in `spek-fu/ai/plugins/skf/skills/config.json`), `meta-knowledge-manage` emits a `distillation-recommended: true` signal.
3. **Signal detection**: The orchestrator's close runbook detects this signal and dispatches `meta-knowledge-distillation`.
4. **Classification**: Lessons are classified as project-specific (kept) or general-recurring (promoted).
5. **Pattern generation**: Clusters of 3+ related general-recurring lessons are generalized into new PT0xx pattern files.
6. **Pattern storage**: New patterns are added to the pattern database.
7. **Cleanup**: Promoted lessons are removed from the knowledge database.
8. **Pattern availability**: The new patterns immediately become available to future orchestration cycles.


## ⚡ Workflow Modes

Spek-Fu supports two primary workflow paths. Both are driven by the same orchestrator and benefit from the same self-learning engine.

---

### Spec-Flow: Spec-Driven Feature Development

Use the **Spec-Flow path** when building a new feature from a raw idea. You drive specification interactively with AI assistance — the orchestrator does not touch code until the full spec package is complete and passes the readiness gate.

```
Human-driven, AI-assisted                  AI-driven, orchestrated
──────────────────────────────────────     ──────────────────────────────────────────
 /spec-feature-draft                        @skf-general-orchestrator
 /spec-clarification                            dispatches → spec-implement
 /spec-devils-advocate                          (phase by phase)
 /spec-testability-draft
 /spec-technical-draft
 /spec-tdd-draft
 /spec-tasks-draft
 /spec-feature-analysis  ← readiness gate ─►  implementation begins
```

**When to use:** Building new features, multi-component or multi-phase work, or any task where upfront clarity prevents costly downstream rework.

See [Spec-Flow Plugin](#-spec-flow-plugin) for the full step-by-step reference.

---

### General Purpose: Direct Orchestration

Use the **general-purpose path** for any request where scope is already clear — refactoring, bug fixes, framework maintenance, exploratory tasks, or anything that does not warrant a full spec pipeline.

```
User request  →  @skf-general-orchestrator  →  wave decomposition  →  impl-implement
```

The orchestrator decomposes the request into ordered waves, selects skills, and dispatches subagents with verification gates — no spec pipeline required.

**When to use:** Scope is clear, refactoring, debugging, framework changes, or exploratory work.

---



## � How-To Guides

### How to Run the Spec-Flow Pipeline

Spec-Flow is a **manual, session-by-session workflow**. Each slash command runs in its own VS Code Chat session — review the output, iterate until satisfied, then open a new session for the next step. Do not chain multiple spec steps in a single session.

**Step-by-step:**

1. **Open a new chat session** for each spec step and run the commands in order:

   | Session | Command | When to move on |
   |---------|---------|------------------|
   | 1 | `/spec-feature-draft` | Spec looks complete and captures your intent |
   | 2 | `/spec-clarification` | All ambiguities resolved; no `[NEEDS CLARIFICATION]` markers remain |
   | 3 | `/spec-devils-advocate` | Findings reviewed; if critical issues found, re-run `/spec-clarification` with report as context, then re-run this step |
   | 4 | `/spec-testability-draft` | Findings reviewed; if non-testable requirements found, re-run `/spec-clarification` with report as context, then re-run this step |
   | 5 | `/spec-technical-draft` | Technical design looks sound |
   | 6 | `/spec-tdd-draft` | TDD contract reviewed |
   | 7 | `/spec-tasks-draft` | Task list looks complete and correctly phased |
   | 8 | `/spec-feature-analysis` | Verdict is `READY` or `READY WITH WARNINGS` |

2. **After a `READY` verdict**, open a **new chat session**, select the orchestrator agent and provide instructions to implement the spec feature.

   The orchestrator reads `tasks.md` and all spec artifacts from the feature directory, then drives `spec-implement` phase by phase until all tasks are complete.

**Key rules:**
- Each slash command is its own fresh chat session.
- The feature directory path (e.g. `spek-fu/features/<feature-name>/`) is the primary input to the orchestrator — it locates `tasks.md`, `spec.md`, and all other artifacts automatically.
- If `spec-feature-analysis` returns `BLOCKED`, resolve the flagged issues and re-run it before handing off.
- You can re-run any step as many times as needed before moving on.

---

### How to Run General-Purpose Work

For tasks with clear, bounded scope — bug fixes, refactoring, framework changes, exploratory tasks — skip the spec pipeline and go directly to the orchestrator.

**Step-by-step:**

1. **Open a new chat session** in VS Code Chat.

2. **Invoke the orchestrator** with your request

3. The orchestrator decomposes the request into ordered waves, selects the appropriate skills, and dispatches subagents to execute each wave with verification gates between them.

4. **Review wave outputs** if the orchestrator pauses for confirmation between phases.

**Key rules:**
- Use this mode when scope is already clear and upfront specification would add no value. Best results are achieved with a pre-generated plan. The native Github /plan agent is highly recommended for this.
- The orchestrator handles all decomposition — you do not need to break the work down manually.
- For large, multi-component, or ambiguous requests, prefer the Spec-Flow pipeline to avoid costly downstream rework.

---



## �📋 Quickstart

1. **Clone** this repository into your project root
2. **Open** in VS Code with GitHub Copilot Chat enabled
3. **Configure** `spek-fu/constitution/` and `spek-fu/project/` with your own content
4. **Use** `@skf-general-orchestrator` for free-form requests, or invoke `/` commands for scoped operations
5. *(Optional)* **Extend** with a custom plugin — see [Creating a Custom Plugin](#creating-a-custom-plugin)


### 🎯 Common Workflows

| Workflow | Approach | Details |
|----------|----------|----------|
| **Spec-driven feature** | Spec-Flow pipeline → `@skf-general-orchestrator` | Step through spec skills interactively; orchestrator drives implementation phase |
| **General-purpose work** | `@skf-general-orchestrator` | Analyzes request, selects skills, sequences work end-to-end |
| **Direct commands** | `/` slash commands | Use when operation is already well-defined |
| **Framework changes** | `/gov-update` | Run after adding/renaming/removing artifacts |
| **Custom plugin** | `create-plugin.py` + `/gov-update` | Scaffold plugin, add skills, sync index |
| **Plugin skills** | `/` slash commands | Every user-facing skill from any registered plugin is available as a slash command |

See [Using Skills as Slash Commands](#using-skills-as-slash-commands) and [Creating a Custom Plugin](#creating-a-custom-plugin) for detailed guidance.


### 🛠️ Framework Management Commands

```
/meta-skill-manage              Create or refine a skill
/meta-knowledge-manage          Capture or retrieve lessons
/meta-knowledge-distillation    Distill lessons into patterns
/meta-script-manage             Create or refine a script
/gov-update                     Run index/documentation synchronization
```


### 🛠️ Framework Management Scripts


**`sync-index-files.py`**  
Syncs all `*-index.json` files with the actual filesystem state:
- Adds new entries
- Removes stale ones
- Extracts frontmatter data
- Preserves existing descriptions

Recommended pre-commit check: `python3 spek-fu/ai/scripts/python/sync-index-files.py --check`.

Run after adding, renaming, or removing any indexed framework artifact.

**Linux/macOS (bash):**
```bash
python3 spek-fu/ai/scripts/python/sync-index-files.py
```

**Windows (PowerShell/CMD):**
```powershell
python spek-fu/ai/scripts/python/sync-index-files.py
```

---

**`generate-prompt-files.py`**  
Generates `.prompt.md` files (one per user-facing skill across all registered plugins) in `.github/prompts/`.  
User-facing skills are all skills except those starting with `orch-` or `impl-`.  
Run after creating or modifying any user-facing skill, or after adding a new plugin.

**Linux/macOS (bash):**
```bash
python3 spek-fu/ai/scripts/python/generate-prompt-files.py
```

**Windows (PowerShell/CMD):**
```powershell
python spek-fu/ai/scripts/python/generate-prompt-files.py
```

---

**`create-plugin.py`**  
Scaffolds a new custom plugin folder under `spek-fu/ai/plugins/` with standard structure:
```
spek-fu/ai/plugins/<plugin-name>/
├── <plugin-name>-index.json
├── knowledge/
├── skills/
└── templates/
```

**Arguments:**
- `--name <plugin-name>` **(required)** — plugin slug (lowercase alphanumeric + hyphens)
- `--dry-run` **(optional)** — preview paths without writing files

**Linux/macOS (bash):**
```bash
python3 spek-fu/ai/scripts/python/create-plugin.py --name <plugin-name>
python3 spek-fu/ai/scripts/python/create-plugin.py --name <plugin-name> --dry-run
```

**Windows (PowerShell/CMD):**
```powershell
python spek-fu/ai/scripts/python/create-plugin.py --name <plugin-name>
python spek-fu/ai/scripts/python/create-plugin.py --name <plugin-name> --dry-run
```



## 🔌 Creating a Custom Plugin

Plugins are the primary **extension point** of the framework. The scaffolding script creates a complete, index-linked plugin structure in one command — **no manual wiring required**.


### What the scaffold creates

```
spek-fu/ai/plugins/<plugin-name>/
├── <plugin-name>-index.json    # Plugin-level index, registered in plugins-index.json
├── knowledge/
│   └── knowledge-index.json   # Ready for domain-specific knowledge files
├── skills/
│   └── skills-index.json      # Ready for skill definitions
└── templates/
    └── templates-index.json   # Ready for scaffolding templates
```

The plugin is automatically registered in `spek-fu/ai/plugins/plugins-index.json` so the orchestrator can traverse into it from the root index chain.


### Step-by-step

```bash
# 1. Preview the scaffold (no files written)
python3 spek-fu/ai/scripts/python/create-plugin.py --name my-plugin --dry-run

# 2. Scaffold the plugin
python3 spek-fu/ai/scripts/python/create-plugin.py --name my-plugin

# 3. Add skill files to spek-fu/ai/plugins/my-plugin/skills/
#    Use /meta-skill-manage to create them following the standard format.

# 4. Register new skills in the index chain
python3 spek-fu/ai/scripts/python/sync-index-files.py
#    Or: run /gov-update — it calls sync automatically.
```

**Windows (PowerShell/CMD):**

```powershell
# 1. Preview the scaffold (no files written)
python spek-fu/ai/scripts/python/create-plugin.py --name my-plugin --dry-run

# 2. Scaffold the plugin
python spek-fu/ai/scripts/python/create-plugin.py --name my-plugin

# 3. Add skill files to spek-fu/ai/plugins/my-plugin/skills/
#    Use /meta-skill-manage to create them following the standard format.

# 4. Register new skills in the index chain
python spek-fu/ai/scripts/python/sync-index-files.py
#    Or: run /gov-update — it calls sync automatically.
```

Once step 4 is complete, `@skf-general-orchestrator` can discover and dispatch your plugin's skills on the next request — the same way it routes to built-in `skf` skills.


### Plugin name rules

The `--name` slug must be lowercase alphanumeric with hyphens (e.g. `dotnet`, `data-pipeline`, `my-domain`). It becomes the folder name and is used in all generated index paths.



## � Spec-Flow Plugin

**Spec-Flow** is a built-in plugin that implements an **eight-step specification pipeline** followed by an orchestrator-driven implementation phase. You drive specification interactively with AI assistance — the orchestrator does not touch code until every artifact is complete and the feature-analysis readiness gate passes. This separation keeps humans in control of *what* gets built while the AI handles *how* to build it.

### Workflow Chain

The pipeline follows a strict dependency order, with each step producing an artifact consumed by the next:

```
spec-feature-draft
      ↓
spec-clarification
      ↓
spec-devils-advocate
      ↓
spec-testability-draft
      ↓
spec-technical-draft
      ↓
spec-tdd-draft
      ↓
spec-tasks-draft
      ↓
spec-feature-analysis
      ↓
@skf-general-orchestrator
  (dispatches → spec-implement)
```

### Ten Steps

| # | Step | Purpose | Output Artifact | Required |
|----|------|---------|-----------------|----------|
| 1 | **spec-feature-draft** | Generate initial feature spec from raw idea | `FEATURE_DIR/spec.md` | ✅ Required |
| 2 | **spec-clarification** | Resolve ambiguities through structured Q&A | `FEATURE_DIR/spec.md` (amended) | ✅ Required |
| 3 | **spec-devils-advocate** | Red-team spec to surface failure modes | `FEATURE_DIR/devils-advocate/devils-advocate-report.md` | 🔶 Strongly recommended |
| 4 | **spec-testability-draft** | Evaluate from test-engineering perspective | `FEATURE_DIR/test-expert/testability-assessment.md` | ✅ Required |
| 5 | **spec-technical-draft** | Produce technical design & architecture decisions | `FEATURE_DIR/research.md`, `FEATURE_DIR/data-model.md`, `FEATURE_DIR/contracts/`, `FEATURE_DIR/quickstart.md` | ✅ Required |
| 6 | **spec-tdd-draft** | Convert testability findings into TDD design | `FEATURE_DIR/tdd-designer/report.md` | ✅ Required |
| 7 | **spec-tasks-draft** | Decompose design into phased, ordered task list | `FEATURE_DIR/tasks.md` | ✅ Required |
| 8 | **spec-feature-analysis** | Surface staleness, unresolved clarifications, and coverage gaps | `FEATURE_DIR/feature-analysis-report.md` | ✅ Required |
| 9 | **spec-implement** | Execute a single task plan phase (dispatched by the orchestrator) | Implementation changes in the feature branch; `FEATURE_DIR/tasks.md` updated | ✅ Required |
| 10 | **@skf-general-orchestrator** | Orchestrate full implementation by dispatching `spec-implement` phase by phase, using all spec artifacts as context | All phases completed; `FEATURE_DIR/tasks.md` fully resolved | ✅ Required |

### Invocation Pattern

The spec-flow pipeline is invoked step by step using slash commands (e.g. `/spec-feature-draft`, `/spec-devils-advocate`). Each step is interactive — you review the output, ask follow-up questions, and iterate before moving to the next step. Once all eight spec steps are complete and the feature-analysis verdict is `READY`, hand off to `@skf-general-orchestrator` for implementation.

### Key Design Principles

- **Fail-fast adversarial review**: Step 3 (devils-advocate) surfaces architectural fragility before downstream planning, reducing rework. The report does not modify the spec — feed findings back through `/spec-clarification` if spec changes are needed.
- **Test-first design**: Step 6 converts testability analysis into a TDD implementation contract that developers follow before writing code. If non-testable requirements are found in step 4, address them via `/spec-clarification` before continuing.
- **Incremental clarity**: `/spec-clarification` is the **only approved mechanism** for modifying `spec.md` at any point in the pipeline — including after receiving adversarial or testability findings.
- **Phased decomposition**: Step 7 produces implementation waves with explicit dependencies and verification criteria.

### Required Execution

All eight specification steps are required. Skipping any step introduces uncompensated risk into specification quality and therefore into implementation accuracy — the orchestrator's output is only as good as the spec it receives.

**Spec amendment rule**: `spec-clarification` is the only step that writes to `spec.md`. Report steps (`spec-devils-advocate`, `spec-testability-draft`) never modify the spec. If either report surfaces issues that require spec changes, re-run `/spec-clarification` with the report as context, then re-run the report step to verify the spec was correctly updated before proceeding.

`spec-feature-analysis` (step 8) is the readiness gate: it surfaces staleness, unresolved clarifications, and coverage gaps before the orchestrator touches any code. It will return `BLOCKED` if `spec.md` was not updated after a report that identified issues requiring spec changes. A `BLOCKED` verdict halts progress until the underlying issues are resolved.

Once the full spec package is ready, `@skf-general-orchestrator` drives implementation by dispatching `spec-implement` phase by phase. Invoking `spec-implement` directly is valid for single-phase execution, but the orchestrator is required for full end-to-end delivery.

### Example: Generating a Feature Spec

For an **API Rate Limiting** feature, you would work through the pipeline manually:

```
1. /spec-feature-draft
   Input: "Per-endpoint rate limiting with configurable thresholds and flexible retry headers"
   Output: FEATURE_DIR/spec.md

2. /spec-clarification
   Input: FEATURE_DIR/spec.md
   Output: FEATURE_DIR/spec.md (amended with clarifications)
   
3. /spec-devils-advocate
   Input: FEATURE_DIR/spec.md
   Output: FEATURE_DIR/devils-advocate/devils-advocate-report.md
   
4. /spec-testability-draft
   Input: FEATURE_DIR with spec.md and devils-advocate report
   Output: FEATURE_DIR/test-expert/testability-assessment.md
   
5. /spec-technical-draft
   Input: FEATURE_DIR with upstream artifacts
   Output: FEATURE_DIR/research.md, FEATURE_DIR/data-model.md, FEATURE_DIR/contracts/, FEATURE_DIR/quickstart.md
   
6. /spec-tdd-draft
   Input: FEATURE_DIR with technical design artifacts
   Output: FEATURE_DIR/tdd-designer/report.md
   
7. /spec-tasks-draft
   Input: FEATURE_DIR with research.md, data-model.md, contracts/, quickstart.md, and spec.md
   Output: FEATURE_DIR/tasks.md

8. /spec-feature-analysis
   Input: FEATURE_DIR with all pipeline artifacts
   Output: FEATURE_DIR/feature-analysis-report.md

9. /spec-implement  (dispatched by orchestrator — not invoked directly for full delivery)
   Input: FEATURE_DIR with tasks.md and design artifacts
   Output: implementation changes for the targeted phase; completed tasks marked in FEATURE_DIR/tasks.md

10. @skf-general-orchestrator
    Input: FEATURE_DIR with tasks.md and all spec artifacts
    Output: all phases implemented end-to-end; FEATURE_DIR/tasks.md fully resolved
```

Each step is invoked interactively, allowing you to review outputs, ask follow-up questions, and iterate before proceeding to the next step. The final `tasks.md` is consumed by `@skf-general-orchestrator`, which drives `spec-implement` phase by phase to deliver the full implementation.



## �💬 Using Skills as Slash Commands

**User-facing skills** (`gov-` and `meta-`) are exposed as slash commands for direct interaction.

**Internal skills** (`orch-` and `impl-`) are routed by the orchestrator and not invoked directly.

This separation ensures the management layer stays accessible while keeping orchestration details internal.


### Interactive Skills

Skills marked **Interactive skill** at the top of their file call `vscode_askQuestions` to collect decisions during execution. All user-facing skills — including all `spec-` pipeline skills — are interactive. When the orchestrator dispatches any of these as a stateless subagent, the approval and decision steps are bypassed and the skill runs non-interactively. When you invoke them directly as slash commands in VS Code Chat, they run fully interactively.


### Commands

| Command | Purpose | Interactive |
|---------|---------|-------------|
| `/gov-update` | Apply governance file updates; always runs index sync at the end | Yes |
| `/meta-knowledge-manage` | Record lessons, surface advisory lessons, or search the knowledge database | Yes |
| `/meta-knowledge-distillation` | Distill general-recurring lessons into PT0xx patterns, or merge duplicate/similar lessons | Yes |
| `/meta-script-manage` | Scaffold and validate framework scripts in `spek-fu/ai/scripts/` | Yes |
| `/meta-skill-manage` | Create, evaluate, and refine skill files | Yes |
| `/spec-feature-draft` | Generate initial feature spec from raw idea | Yes |
| `/spec-clarification` | Resolve ambiguities in a spec through structured Q&A | Yes |
| `/spec-devils-advocate` | Red-team spec to surface failure modes and assumptions | Yes |
| `/spec-testability-draft` | Evaluate spec from a test-engineering perspective | Yes |
| `/spec-technical-draft` | Produce technical design, contracts, and data model | Yes |
| `/spec-tdd-draft` | Convert testability findings into a TDD implementation design | Yes |
| `/spec-tasks-draft` | Decompose design into phased, dependency-ordered task list | Yes |
| `/spec-feature-analysis` | Validate all spec artifacts and produce readiness verdict | Yes |
| `/spec-implement` | Execute a single implementation phase (single-phase use; full delivery requires orchestrator) | Yes |

### Usage Examples

```
/gov-update update docs based on files changes
/meta-knowledge-manage write "Always read devcontainer-guidelines.md before writing files in this environment."
/meta-knowledge-distillation distill
/meta-knowledge-distillation merge
/meta-skill-manage create "A skill that validates ADR structure against the ADR template"
/meta-script-manage validate spek-fu/ai/scripts/python/sync-index-files.py
```


### Agent Tier Architecture

| Agent | Tier | User Invocable | Model | Best For |
|-------|------|-----------|-------|----------|
| **`skf-general-orchestrator`** | Orchestrator | ✅ Yes | Claude Sonnet 4.6 | Routing & decomposition |
| **`fast-agent`** | Tier 1 | No | Claude Haiku 4.5 | Speed-critical tasks |
| **`standard-agent`** | Tier 2 | No | Claude Sonnet 4.6 | General purpose work |
| **`large-context-agent`** | Tier 3 | No | GPT-5.4 | Large context needs |



## 🐳 Dev Containers

Spek-Fu works best **inside a dev container** for:
- **Isolation**: Keep agent mistakes in a contained environment
- **Safety**: Terminal auto-approve is safer in containers
- **Reproducibility**: Consistent toolchains across all contributors
- **Convenience**: Framework-required tools pre-installed


### Installation steps

1. **Install prerequisites**
   - Install [Docker Desktop](https://www.docker.com/products/docker-desktop) for your OS (Windows, macOS, or Linux).
   - Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code.

2. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd spek-fu
   ```

3. **Open in dev container**
   - Open the workspace folder in VS Code.
   - Make sure you have a `devcontainer.json` file in `.devcontainer/` folder with your desired settings. A default file will be provided for minimum requirements for the framework.
   - VS Code will detect the `.devcontainer/` folder and prompt you to reopen in a container.
   - Click **Reopen in Container** or use the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and run **Dev Containers: Reopen in Container**.
   - Wait for the container to build and initialize (first build takes a few minutes; subsequent opens are faster).

4. **Verify the setup**
   - Confirm GitHub Copilot Chat is enabled in VS Code.
   - Open a terminal and verify tools are available: `git --version`, `python3 --version`, `gh --version`.
   - You're ready to use the framework. Start with `@skf-general-orchestrator` for any task.


### Environment Config

`skf-config.json` controls environment mode for the framework.

- Use `"environment": "devcontainer"` to require devcontainer execution.
- Use `"environment": "host"` to force host-mode behavior.
- Leave `"environment": "auto"` to detect the runtime environment by AI.



## 📑 Progressive Disclosure Index System

Spek-Fu uses a **hierarchical index chain** to enable **progressive disclosure**:
- Agents load only needed metadata at each layer
- Follow the index chain downward only when required
- Keeps context **lean**
- Speeds up **navigation**
- Prevents **information overload**


### Navigation Pattern

Example traversal chain:

```text
skf-root-index.json
   -> spek-fu/ai/ai-index.json
      -> spek-fu/ai/plugins/plugins-index.json
         -> spek-fu/ai/plugins/skf/skf-index.json
            -> spek-fu/ai/plugins/skf/skills/skills-index.json
               -> spek-fu/ai/plugins/skf/skills/meta-knowledge-distillation.md
```

Loads each index only when needed to navigate into that layer. Stops as soon as the file or folder needed is found.



## 📂 Folder Structure

**Structural organization of the workspace.** For the narrative flow of component interactions at runtime, see [Orchestration Flow](#orchestration-flow).

```text
/
├── skf-root-index.json              # Root index — entry point for the index-driven loading chain
├── context.md                       # Working context artifact for session management
├── skf-config.json                  # Runtime environment mode (auto | devcontainer | host)
├── spek-fu/
│   ├── constitution/                # Project governance
│   │   └── constitution.md          # Consolidated governance: principles, standards, guidelines
│   ├── project/                     # Project documentation
│   │   └── project.md               # Consolidated specification: business requirements and technical design
│   ├── ai/                          # AI framework
│   │   ├── ai-index.json            # AI-level index — links scripts and plugins
│   │   ├── scripts/
│   │   │   └── python/              # Python automation and validation scripts
│   │   └── plugins/
│   │       ├── skf/                 # Built-in plugin — skills, runbooks, knowledge, patterns, and support assets
│   │       │   ├── knowledge/       # Reference databases and guidance files
│   │       │   ├── patterns/        # Behavioral patterns and tag vocabularies
│   │       │   ├── runbooks/        # Dispatch contract and phase procedures
│   │       │   ├── skills/          # Skill definitions across 4 groups
│   │       │   └── templates/       # Framework authoring and orchestration templates
│   │       └── <custom-plugin>/     # Your own plugin (scaffolded via create-plugin.py)
│   │           ├── knowledge/       # Domain-specific knowledge files
│   │           ├── skills/          # Custom skill definitions (auto-discovered via index chain)
│   │           └── templates/       # Custom scaffolding templates
│   ├── features/                    # Spec-flow feature workspaces
│   └── reports/                     # Analysis output (auto-generated, git-tracked)
├── .github/
│   ├── copilot-instructions.md      # Bootstrap Copilot context — SSOT pointers only
│   ├── agents/                      # Canonical agent definitions used by VS Code chat
│   └── prompts/                     # Canonical slash commands (all plugin skills except orch-* and impl-*)
└── .vscode/
    └── settings.json                # VS Code configuration
```



## 🏗️ Framework Components

### Skills

**Skills** are the atomic behavioral units of the SKF AI framework:
- Structured `.md` files defining complete, self-contained workflows
- Pattern: **Inputs → Steps → Outputs**
- Dispatched by orchestrators via Dispatch Contract
- Executed by subagents in clean-slate sessions

| Group | Purpose | Invocable |
|-------|---------|----------|
| **`meta-`** | Framework lifecycle & maintenance | ✅ Slash commands |
| **`gov-`** | Governance changes w/ approval | ✅ Slash commands |
| **`spec-`** | Feature specification pipeline | ✅ Slash commands |
| **`orch-`** | Orchestration & cross-skill services | Internal only |
| **`impl-`** | Code execution & implementation | Internal only |

> Any skill not starting with `orch-` or `impl-` is automatically available as a slash command, regardless of plugin or prefix.


### Patterns

**Patterns** are reusable behavioral rules for AI agent orchestration:
- Selected & bundled by the orchestration layer
- Created automatically via self-learning distillation loop
- Promoted manually via `meta-knowledge-distillation`
- Stored as **PT0xx** files in `spek-fu/ai/plugins/skf/patterns/`

📌 **Authoritative inventory:** `spek-fu/ai/plugins/skf/patterns/patterns-index.json`


### Runbooks

**Runbooks** are per-phase orchestrator execution guides:
- **Shared rules:** `spek-fu/ai/plugins/skf/runbooks/runbook-shared.md`
- **Phase-specific rules:** co-located in same folder


### Knowledge Base

**Knowledge base** — collection of reference databases, taxonomies, and advisory documents used by skills and orchestrators via just-in-time retrieval.

📌 **Authoritative inventory:** `spek-fu/ai/plugins/skf/knowledge/knowledge-index.json`


### Templates

**Templates** scaffold framework components and orchestration artifacts.

📌 **Authoritative inventory:** `spek-fu/ai/plugins/skf/templates/templates-index.json`


### Scripts

**Python helper scripts** under `spek-fu/ai/scripts/python/` support:
- Index traversal
- Validation
- Frontmatter-driven discovery

📌 **Authoritative inventory:** `spek-fu/ai/scripts/python/python-index.json`  
📌 **Quick reference:** [Scripts Cheat Sheet](#scripts-cheat-sheet)


### Commands

**Commands** are VS Code slash commands (`.prompt.md` files) providing direct user-facing entry points:
- All skills exposed as slash commands except `orch-` and `impl-` (internal dispatch only)
- Stored in `.github/prompts/`

📌 **Authoritative inventory:** `.github/prompts/prompts-index.json`


### Dispatch System

**Dispatch system** — protocol for orchestrators invoking skill-executing subagents.

**Enforces:**
- Clean-slate subagent calls
- Structured manifest formatting
- Agent-tier routing
- Verification gates

**Defined in:**
- `spek-fu/ai/plugins/skf/runbooks/`
- `spek-fu/ai/plugins/skf/templates/`


### Plugins

**Plugins** are the extension unit of the framework:
- Built-in plugin (`skf`) at `spek-fu/ai/plugins/skf/`
- Add unlimited custom plugins with `skills/`, `knowledge/`, `templates/` sub-folders
- Each plugin is independently discoverable

**Auto-discovery workflow:**
1. Orchestrator traverses index chain starting from `skf-root-index.json`
2. `plugins-index.json` lists registered plugins
3. Each plugin's `skills-index.json` lists available skills
4. **Any registered skill is immediately available for dispatch** — no manual wiring needed


## 📚 Documentation Philosophy

Framework documentation is organized into **three branches**:

| Branch | Location | Contains |
|--------|----------|----------|
| **Constitution** | `spek-fu/constitution/` | Governance principles, project constraints, coding standards, non-negotiable rules |
| **Project** | `spek-fu/project/` | Project specs, documentation, business requirements, technical decisions, ADRs |
| **Framework** | `spek-fu/ai/`, `spek-fu/reports/`, roots | Skills, agents, templates, runbooks, indexes, generated reports |




