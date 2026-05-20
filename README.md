# 🚀 Spek-Fu

> **A self-learning agent orchestration system that grows with your project.**

Spek-Fu is an **AI agentic development framework** built around a general-purpose orchestrator that:
- Decomposes requests into **subagent waves**
- Routes each wave through a **tiered agent pool**
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
| **Knowledge** `ai/plugins/skf/knowledge/` | Operation-specific lessons (project-scoped) | "Always read devcontainer-guidelines.md before writing" |
| **Patterns** `ai/plugins/skf/patterns/` | Reusable behavioral strategies (PT0xx files) | PT007: Just-in-Time Retrieval, PT023: Parallelization |

**Key distinction:** Lessons are specific & operational (stay local) • Patterns are general & structural (travel across projects)


### Self-Learning Loop

1. **Lessons accumulate** in `knowledge-database.md` through normal operation.
2. **Threshold check**: When the lesson count reaches the configured threshold (`knowledgeDistillationThreshold` in `ai/plugins/skf/skills/config.json`), `meta-knowledge-manage` emits a `distillation-recommended: true` signal.
3. **Signal detection**: The orchestrator's close runbook detects this signal and dispatches `meta-knowledge-distillation`.
4. **Classification**: Lessons are classified as project-specific (kept) or general-recurring (promoted).
5. **Pattern generation**: Clusters of 3+ related general-recurring lessons are generalized into new PT0xx pattern files.
6. **Pattern storage**: New patterns are added to the pattern database.
7. **Cleanup**: Promoted lessons are removed from the knowledge database.
8. **Pattern availability**: The new patterns immediately become available to future orchestration cycles.



## Orchestration Flow

1. **Request intake**: A request enters `@skf-general-orchestrator`.
2. **Index traversal**: The orchestrator reads the intake runbook and traverses the index chain to locate applicable skills and patterns.
3. **Plan production**: An orchestration plan is created and decomposed into ordered waves.
4. **Wave dispatch**: Each wave is dispatched as a clean-slate subagent with a structured manifest (skill, inputs, agent tier, verification criteria).
5. **Skill execution**: Subagents execute the skill protocol exactly and return structured output.
6. **Output verification**: The orchestrator verifies each output against the wave's acceptance criteria before advancing.
7. **Lesson capture**: After all waves complete, the close runbook captures lessons via `meta-knowledge-manage`.
8. **Distillation check**: If the distillation threshold is crossed, `meta-knowledge-distillation` is dispatched to distill accumulated lessons into new patterns.
9. **Pattern feedback**: New patterns feed back into future orchestration cycles, compounding the system's behavioral repertoire over time.



## 📋 Quickstart

1. **Clone** this repository into your project root
2. **Open** in VS Code with GitHub Copilot Chat enabled
3. **Configure** `constitution/` and `project/` with your own content
4. **Use** `@skf-general-orchestrator` for free-form requests, or invoke `/` commands for scoped operations
5. *(Optional)* **Extend** with a custom plugin — see [Creating a Custom Plugin](#creating-a-custom-plugin)


### 🎯 Common Workflows

| Workflow | Approach | Details |
|----------|----------|----------|
| **Free-form requests** | `@skf-general-orchestrator` | Analyzes request, selects skills, sequences work end-to-end |
| **Direct commands** | `/` slash commands | Use when operation is already well-defined |
| **Framework changes** | `/gov-update` | Run after adding/renaming/removing artifacts |
| **Custom plugin** | `create-plugin.py` + `/gov-update` | Scaffold plugin, add skills, sync index |

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

Run after adding, renaming, or removing any indexed framework artifact.

**Linux/macOS (bash):**
```bash
python3 ai/scripts/python/sync-index-files.py
```

**Windows (PowerShell/CMD):**
```powershell
python ai/scripts/python/sync-index-files.py
```

---

**`generate-prompt-files.py`**  
Generates `.prompt.md` files (one per `gov-` or `meta-` skill) in `.github/prompts/`.  
Run after creating or modifying a `gov-` or `meta-` skill.

**Linux/macOS (bash):**
```bash
python3 ai/scripts/python/generate-prompt-files.py
```

**Windows (PowerShell/CMD):**
```powershell
python ai/scripts/python/generate-prompt-files.py
```

---

**`create-plugin.py`**  
Scaffolds a new custom plugin folder under `ai/plugins/` with standard structure:
```
ai/plugins/<plugin-name>/
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
python3 ai/scripts/python/create-plugin.py --name <plugin-name>
python3 ai/scripts/python/create-plugin.py --name <plugin-name> --dry-run
```

**Windows (PowerShell/CMD):**
```powershell
python ai/scripts/python/create-plugin.py --name <plugin-name>
python ai/scripts/python/create-plugin.py --name <plugin-name> --dry-run
```



## 🔌 Creating a Custom Plugin

Plugins are the primary **extension point** of the framework. The scaffolding script creates a complete, index-linked plugin structure in one command — **no manual wiring required**.


### What the scaffold creates

```
ai/plugins/<plugin-name>/
├── <plugin-name>-index.json    # Plugin-level index, registered in plugins-index.json
├── knowledge/
│   └── knowledge-index.json   # Ready for domain-specific knowledge files
├── skills/
│   └── skills-index.json      # Ready for skill definitions
└── templates/
    └── templates-index.json   # Ready for scaffolding templates
```

The plugin is automatically registered in `ai/plugins/plugins-index.json` so the orchestrator can traverse into it from the root index chain.


### Step-by-step

```bash
# 1. Preview the scaffold (no files written)
python3 ai/scripts/python/create-plugin.py --name my-plugin --dry-run

# 2. Scaffold the plugin
python3 ai/scripts/python/create-plugin.py --name my-plugin

# 3. Add skill files to ai/plugins/my-plugin/skills/
#    Use /meta-skill-manage to create them following the standard format.

# 4. Register new skills in the index chain
python3 ai/scripts/python/sync-index-files.py
#    Or: run /gov-update — it calls sync automatically.
```

**Windows (PowerShell/CMD):**

```powershell
# 1. Preview the scaffold (no files written)
python ai/scripts/python/create-plugin.py --name my-plugin --dry-run

# 2. Scaffold the plugin
python ai/scripts/python/create-plugin.py --name my-plugin

# 3. Add skill files to ai/plugins/my-plugin/skills/
#    Use /meta-skill-manage to create them following the standard format.

# 4. Register new skills in the index chain
python ai/scripts/python/sync-index-files.py
#    Or: run /gov-update — it calls sync automatically.
```

Once step 4 is complete, `@skf-general-orchestrator` can discover and dispatch your plugin's skills on the next request — the same way it routes to built-in `skf` skills.


### Plugin name rules

The `--name` slug must be lowercase alphanumeric with hyphens (e.g. `dotnet`, `data-pipeline`, `my-domain`). It becomes the folder name and is used in all generated index paths.



## � Spec-Flow Plugin

**Spec-Flow** is a built-in plugin that implements an **eight-step feature specification pipeline**, transforming raw ideas into implementation-ready task lists through structured, adversarial review and test-driven design.

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
spec-tdd-draft
      ↓
spec-technical-draft
      ↓
spec-tasks-draft
   ↓
spec-implement
```

### Eight Steps

| # | Step | Purpose | Output Artifact | Required |
|----|------|---------|-----------------|----------|
| 1 | **spec-feature-draft** | Generate initial feature spec from raw idea | `FEATURE_DIR/spec.md` | ✅ Required |
| 2 | **spec-clarification** | Resolve ambiguities through structured Q&A | `FEATURE_DIR/spec.md` (amended) | ✅ Required |
| 3 | **spec-devils-advocate** | Red-team spec to surface failure modes | `FEATURE_DIR/devils-advocate/devils-advocate-report.md` | 🔶 Strongly recommended |
| 4 | **spec-testability-draft** | Evaluate from test-engineering perspective | `FEATURE_DIR/test-expert/testability-assessment.md` | ✅ Required |
| 5 | **spec-tdd-draft** | Convert testability findings into TDD design | `FEATURE_DIR/tdd-designer/report.md` | ✅ Required |
| 6 | **spec-technical-draft** | Produce technical design & architecture decisions | `FEATURE_DIR/research.md`, `FEATURE_DIR/data-model.md`, `FEATURE_DIR/contracts/`, `FEATURE_DIR/quickstart.md` | ✅ Required |
| 7 | **spec-tasks-draft** | Decompose design into phased, ordered task list | `FEATURE_DIR/tasks.md` | ✅ Required |
| 8 | **spec-implement** | Execute the task plan phase by phase | Implementation changes in the feature branch; `FEATURE_DIR/tasks.md` updated | ✅ Required |

### Invocation Pattern

The spec-flow pipeline is best invoked manually using prompt slash commands like `/spec-devils-advocate`, since there is a lot of user interaction involved in this flow.

### Key Design Principles

- **Fail-fast adversarial review**: Step 3 (devils-advocate) surfaces architectural fragility before downstream planning, reducing rework.
- **Test-first design**: Step 5 converts testability analysis into a TDD implementation contract that developers follow before writing code.
- **Incremental clarity**: Step 2 (clarification) prevents ambiguities from cascading into every downstream artifact.
- **Phased decomposition**: Step 7 produces implementation waves with explicit dependencies and verification criteria.

### Required Execution

All eight steps are required for the canonical spec-flow pipeline. Skipping any step introduces uncompensated risk into specification quality and implementation accuracy.

### Example: Generating a Feature Spec

For an **API Rate Limiting** feature, you would work through the pipeline manually:

```
1. /spec-feature-draft
   Input: "Per-endpoint rate limiting with configurable thresholds and flexible retry headers"
   Output: FEATURE_DIR/spec.md

2. /spec-clarification
   Input: FEATURE_DIR/spec.md
   Output: Amended spec.md with clarifications
   
3. /spec-devils-advocate
   Input: FEATURE_DIR/spec.md
   Output: FEATURE_DIR/devils-advocate/devils-advocate-report.md
   
4. /spec-testability-draft
   Input: FEATURE_DIR with spec.md and devils-advocate report
   Output: FEATURE_DIR/test-expert/testability-assessment.md
   
5. /spec-tdd-draft
   Input: FEATURE_DIR with testability assessment
   Output: FEATURE_DIR/tdd-designer/report.md
   
6. /spec-technical-draft
   Input: FEATURE_DIR with upstream artifacts
   Output: FEATURE_DIR/research.md, FEATURE_DIR/data-model.md, FEATURE_DIR/contracts/, FEATURE_DIR/quickstart.md
   
7. /spec-tasks-draft
   Input: FEATURE_DIR with research.md, data-model.md, contracts/, quickstart.md, and spec.md
   Output: FEATURE_DIR/tasks.md

8. /spec-implement
   Input: FEATURE_DIR with tasks.md and optional upstream design artifacts
   Output: implementation changes in the feature branch and completed tasks marked in FEATURE_DIR/tasks.md
```

Each step is invoked interactively, allowing you to review outputs, ask follow-up questions, and iterate before proceeding to the next step. The final `tasks.md` is then executed by `spec-implement`.



## �💬 Using Skills as Slash Commands

**User-facing skills** (`gov-` and `meta-`) are exposed as slash commands for direct interaction.

**Internal skills** (`orch-` and `impl-`) are routed by the orchestrator and not invoked directly.

This separation ensures the management layer stays accessible while keeping orchestration details internal.


### Interactive Skills

Skills marked **Interactive skill** at the top of their file call `vscode_askQuestions` to collect decisions during execution. All four user-facing skills are interactive. When the orchestrator dispatches any of these as a stateless subagent, the approval and decision steps are bypassed and the skill runs non-interactively. When you invoke them directly as slash commands in VS Code Chat, they run fully interactively.


### Commands

| Command | Purpose | Interactive |
|---------|---------|-------------|
| `/gov-update` | Apply governance file updates; always runs index sync at the end | Yes |
| `/meta-knowledge-manage` | Record lessons, surface advisory lessons, or search the knowledge database | Yes |
| `/meta-knowledge-distillation` | Distill general-recurring lessons into PT0xx patterns, or merge duplicate/similar lessons | Yes |
| `/meta-script-manage` | Scaffold and validate framework scripts in `ai/scripts/` | Yes |
| `/meta-skill-manage` | Create, evaluate, and refine skill files | Yes |

### Usage Examples

```
/gov-update update docs based on files changes
/meta-knowledge-manage write "Always read devcontainer-guidelines.md before writing files in this environment."
/meta-knowledge-distillation distill
/meta-knowledge-distillation merge
/meta-skill-manage create "A skill that validates ADR structure against the ADR template"
/meta-script-manage validate ai/scripts/python/sync-index-files.py
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
  -> ai/ai-index.json
    -> ai/plugins/plugins-index.json
      -> ai/plugins/skf/skf-index.json
        -> ai/plugins/skf/skills/skills-index.json
          -> ai/plugins/skf/skills/meta-knowledge-distillation.md
```

Loads each index only when needed to navigate into that layer. Stops as soon as the file or folder needed is found.



## 📂 Folder Structure

**Structural organization of the workspace.** For the narrative flow of component interactions at runtime, see [Orchestration Flow](#orchestration-flow).

```text
/
├── skf-root-index.json              # Root index — entry point for the index-driven loading chain
├── context.md                       # Working context artifact for session management
├── skf-config.json                  # Runtime environment mode (auto | devcontainer | host)
├── constitution/                    # Project governance (sub-file structure)
│   ├── constitution.md              # Main file — sub-file table, loading rules
│   ├── governance.md                # Project governance rules
│   ├── company-principles.md        # Organization values and culture
│   ├── project-constraints.md       # Tech stack and architecture boundaries
│   ├── coding-standards.md          # Principles-level coding standards
│   ├── testing-guidelines.md        # Test strategy, coverage, naming
│   └── ai-behavior.md               # Agent constraints and scope limits
├── project/                         # Project documentation
│   ├── project-spec.md              # High-level project specification
│   ├── business-requirements.md     # Business goals, stakeholders, use cases
│   ├── technical-spec.md            # Technical architecture and design decisions
│   └── adrs/                        # Architectural decision records
├── ai/                              # AI framework
│   ├── ai-index.json                # AI-level index — links scripts and plugins
│   ├── scripts/
│   │   └── python/                  # Python automation and validation scripts
│   └── plugins/
│       ├── skf/                     # Built-in plugin — skills, runbooks, knowledge, patterns, and support assets
│       │   ├── knowledge/           # Reference databases and guidance files
│       │   ├── patterns/            # Behavioral patterns and tag vocabularies
│       │   ├── runbooks/            # Dispatch contract and phase procedures
│       │   ├── skills/              # Skill definitions across 4 groups
│       │   └── templates/           # Framework authoring and orchestration templates
│       └── <custom-plugin>/         # Your own plugin (scaffolded via create-plugin.py)
│           ├── knowledge/           # Domain-specific knowledge files
│           ├── skills/              # Custom skill definitions (auto-discovered via index chain)
│           └── templates/           # Custom scaffolding templates
├── reports/                         # Analysis output (auto-generated, git-tracked)
├── .github/
│   ├── copilot-instructions.md      # Bootstrap Copilot context — SSOT pointers only
│   ├── agents/                      # Canonical agent definitions used by VS Code chat
│   └── prompts/                     # Canonical slash commands (gov-* and meta-* only)
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
| **`orch-`** | Orchestration & cross-skill services | Internal only |
| **`impl-`** | Code execution & implementation | Internal only |


### Patterns

**Patterns** are reusable behavioral rules for AI agent orchestration:
- Selected & bundled by the orchestration layer
- Created automatically via self-learning distillation loop
- Promoted manually via `meta-knowledge-distillation`
- Stored as **PT0xx** files in `ai/plugins/skf/patterns/`

📌 **Authoritative inventory:** `ai/plugins/skf/patterns/patterns-index.json`


### Runbooks

**Runbooks** are per-phase orchestrator execution guides:
- **Shared rules:** `ai/plugins/skf/runbooks/runbook-shared.md`
- **Phase-specific rules:** co-located in same folder


### Knowledge Base

**Knowledge base** — collection of reference databases, taxonomies, and advisory documents used by skills and orchestrators via just-in-time retrieval.

📌 **Authoritative inventory:** `ai/plugins/skf/knowledge/knowledge-index.json`


### Templates

**Templates** scaffold framework components and orchestration artifacts.

📌 **Authoritative inventory:** `ai/plugins/skf/templates/templates-index.json`


### Scripts

**Python helper scripts** under `ai/scripts/python/` support:
- Index traversal
- Validation
- Frontmatter-driven discovery

📌 **Authoritative inventory:** `ai/scripts/python/python-index.json`  
📌 **Quick reference:** [Scripts Cheat Sheet](#scripts-cheat-sheet)


### Commands

**Commands** are VS Code slash commands (`.prompt.md` files) providing direct user-facing entry points:
- Only `gov-` and `meta-` skills exposed
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
- `ai/plugins/skf/runbooks/`
- `ai/plugins/skf/templates/`


### Plugins

**Plugins** are the extension unit of the framework:
- Built-in plugin (`skf`) at `ai/plugins/skf/`
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
| **Constitution** | `constitution/` | Governance principles, project constraints, coding standards, non-negotiable rules |
| **Project** | `project/` | Project specs, business requirements, technical decisions, ADRs |
| **Framework** | `ai/`, `reports/`, roots | Skills, agents, templates, runbooks, indexes, generated reports |

---

**Navigation SSOT:** Co-located `*-index.json` files own folder inventories and machine-readable traversal.  
**Human-facing guide:** This `README.md` serves as overview, quickstart, and workflow reference.



