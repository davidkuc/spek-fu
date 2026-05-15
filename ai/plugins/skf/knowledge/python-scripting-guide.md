# Python Scripting Guide

A guide for engineers in mixed-OS environments. Part 1 helps you decide *whether* Python is the right tool for the task. Part 2 covers *how* to use it well once you've decided.

> **Companion document:** `powershell-scripting-guide.md`. The two guides are structured identically — read them side-by-side when a task is genuinely ambiguous.

---

## Part 1 — When to Choose Python (Assessment)

### 1.1 Python's identity in one paragraph

Python is a general-purpose, interpreted, cross-platform programming language. It is not a shell. It is at its best when the task is *building something* — a cross-platform tool, a data pipeline, a script that orchestrates many APIs, a piece of glue inside a larger system — rather than *driving an OS interactively*. Python's leverage comes from three things: cross-platform consistency, an enormous library ecosystem (PyPI), and a syntax that most developers can read on first contact.

### 1.2 Strong-fit signals — pick Python

If two or more of these apply, Python is almost certainly the right tool:

- **The script must run on Linux, macOS, and Windows** with minimal per-OS branching.
- **The task targets non-Microsoft systems** — AWS, GCP, Kubernetes, Linux servers, network devices, third-party SaaS APIs.
- **Data work is involved** — parsing large logs, transforming JSON/CSV/XML, statistical aggregation, generating reports or charts.
- **Significant program logic** beyond shell-style "call command, check exit code, call next command" — real algorithms, state machines, complex branching.
- **The script is expected to grow** into a tool, package, CLI, or service. Python scales from a 30-line script to a 30,000-line application without changing language.
- **The team is heterogeneous** — developers on Mac/Linux, data folks, junior engineers. Python is the lowest common denominator.
- **A Python library already does most of the work** (`boto3`, `requests`, `pandas`, `psutil`, `paramiko`, the cloud SDKs, ML stacks). Re-implementing this elsewhere is wasted effort.
- **The script will be embedded** inside a larger Python codebase, an Ansible playbook, a Jupyter notebook, or a tool that hosts Python.

### 1.3 Weak-fit signals — reconsider

If two or more of these apply, PowerShell (or sometimes Bash) is probably the better choice:

- The task is **pure Windows administration** — Active Directory, Exchange, the registry, event logs, Group Policy, IIS, Windows services.
- The task is **interactive shell work** — quickly listing processes, restarting a service, exploring system state. Python is not a shell; reaching for it here means writing 10 lines where 1 cmdlet would do.
- You'd end up **shelling out to PowerShell from Python anyway** because the underlying capability lives in a PowerShell module. That's an indication the script should just *be* PowerShell.
- The pipeline / surrounding context is **already entirely PowerShell** and adding Python introduces a runtime dependency that doesn't earn its keep.
- The task uses **Microsoft-only services** (Exchange Online, SharePoint Online, Microsoft Graph in admin contexts, Intune). Official, well-supported PowerShell modules exist; Python equivalents are thinner.

### 1.4 Decision questions (use in this order)

1. **Will this run on more than one OS?** → Python.
2. **Does the core work happen on Windows admin surfaces (AD, Exchange, registry, services, GPO)?** → PowerShell.
3. **Is the work data-heavy or algorithmic?** → Python.
4. **Is the work mostly orchestrating existing CLIs/cmdlets on Windows?** → PowerShell.
5. **Is there an existing solution in one of the languages?** → Don't rewrite. Use what works and integrate at a clean boundary.
6. **None of the above gave a clear answer?** → Pick the language your team knows best. Both can do most general-purpose tasks adequately.

### 1.5 Decision matrix

| Scenario | Lean Python | Lean PowerShell |
|---|---|---|
| Cross-platform CLI tool | ✅ | ❌ |
| Active Directory user provisioning | ❌ | ✅ |
| Multi-cloud automation (AWS + Azure + GCP) | ✅ | ⚠️ Possible but thinner |
| Exchange / Microsoft 365 admin | ❌ | ✅ |
| Log parsing & analytics across many servers | ✅ | ⚠️ OK for small jobs |
| Windows registry / event log manipulation | ❌ | ✅ |
| REST API client that becomes a service | ✅ | ❌ |
| One-off ad-hoc shell task | ⚠️ Heavy for this | ✅ |
| Build/test orchestration on Linux CI agents | ✅ | ⚠️ Works if pwsh is installed |
| ML training pipeline | ✅ | ❌ |
| Scripted Azure DevOps task with Az module | ❌ | ✅ |
| Embedding scripting into a third-party app | ✅ | ❌ |
| Network device automation (Netmiko, NAPALM) | ✅ | ❌ |

### 1.6 The mixing rule

Use both, but never mix them inside the same script for the same concern. The healthy pattern is **one orchestrator language, with the other invoked at a clearly defined boundary**. For example: a PowerShell pipeline step that calls `python train.py` and reads its stdout, or a Python tool that calls `pwsh -Command Get-ADUser ...` for one specific Windows-only fetch and parses the JSON result. Avoid scripts where reading them requires fluency in both.

---

## Part 2 — Best Practices and Optimizations

### 2.1 The 2026 default stack

Use the current stack. It is faster, simpler, and has substantially less configuration than what was standard in 2021–2023.

| Concern | Tool | Replaces |
|---|---|---|
| Python install, venv, deps, lockfile, runner | **uv** | pyenv, pip, virtualenv/venv, pip-tools, pipx, poetry |
| Lint + format + import sort | **Ruff** | flake8, black, isort, pyupgrade, pydocstyle |
| Static type checking | **Ty** (or **Pyright** / **mypy**) | mypy alone |
| Test runner | **pytest** | unittest |
| Project config | **`pyproject.toml`** (PEP 621) | `setup.py`, `setup.cfg`, `requirements.txt` |

Pick one Python version per project, pin it in a `.python-version` file, and let `uv` install it. Don't rely on the OS Python.

### 2.2 Project structure

For anything beyond a one-file utility, use this skeleton:

```
my-tool/
├── pyproject.toml          # Single source of truth: deps, ruff, pytest, ty config
├── uv.lock                 # Committed. Locks exact dep versions across machines.
├── .python-version         # Pins the interpreter
├── README.md
├── src/
│   └── my_tool/
│       ├── __init__.py
│       ├── __main__.py     # Enables `python -m my_tool`
│       ├── cli.py          # Argument parsing only
│       ├── core.py         # Business logic — no I/O, no argparse
│       └── io.py           # Files, network, subprocess
└── tests/
    └── test_core.py
```

**The `src/` layout** prevents accidental imports from the project root and forces tests to use the installed package, which catches packaging bugs early.

**Separate logic from I/O.** Functions in `core.py` should take plain data and return plain data. The "shell" — `cli.py`, `io.py` — handles argparse, files, HTTP, subprocesses. This makes core logic trivial to unit-test and easy to reason about.

### 2.3 Dependencies

- **Lock everything.** Commit `uv.lock`. Without it, "works on my machine" is not a joke, it's a guarantee.
- **Use `pyproject.toml`, not `requirements.txt`.** Declare runtime deps under `[project] dependencies` and dev tools under `[dependency-groups] dev`.
- **Don't pin to exact versions in `pyproject.toml`** — pin in the lockfile. Use `>=X.Y` style constraints in the manifest so `uv lock --upgrade` works as expected.
- **Use `uvx` for one-off tools** (`uvx ruff check .`) so you don't pollute the project venv with tooling you don't import.
- **Inline script metadata** (PEP 723) is excellent for single-file utilities you want to share:

  ```python
  # /// script
  # requires-python = ">=3.12"
  # dependencies = ["requests", "rich"]
  # ///
  import requests
  from rich import print
  ...
  ```

  Run with `uv run script.py` — it builds an ephemeral venv automatically.

### 2.4 Code style and idioms

- **Format with Ruff** (`ruff format`). It is Black-compatible. Don't argue about style; let the formatter decide.
- **Lint with Ruff** (`ruff check --fix`). Enable rule sets `E, F, W, I, UP, B, SIM, COM812` at minimum. `UP` (pyupgrade) auto-modernizes syntax as you write.
- **Use type hints on all public function signatures.** Type hints are not optional in 2026 — they are documentation, IDE support, and bug prevention. Internal helpers don't need them, but anything another module calls does.
- **Use `pathlib.Path`, not `os.path`.** `Path("config") / "settings.json"` reads better and works the same on every OS.
- **Use f-strings.** Not `%`, not `.format()`. Python 3.12+ supports inline debugging: `f"{value=}"`.
- **Prefer composition over inheritance.** Use `@dataclass` (or `pydantic.BaseModel` when you need validation) for data containers. Reach for classes when you need to bundle state with behavior; reach for functions otherwise.
- **Use generators for streams.** `(line for line in file if ...)` keeps memory flat. Lists materialize the whole sequence — fine for small inputs, dangerous for large ones.
- **Use the standard library before reaching for a dependency.** `collections`, `itertools`, `functools`, `pathlib`, `dataclasses`, `concurrent.futures`, `json`, `csv`, `argparse`, `logging`, `tomllib` cover an enormous surface area.
- **Use `match` statements** (Python 3.10+) for genuine pattern matching, not as a glorified `if/elif` chain.

### 2.5 Error handling

- **Catch specific exceptions.** `except Exception:` is almost always wrong. `except (FileNotFoundError, PermissionError):` is a real handler.
- **Raise meaningful exceptions.** Define a small hierarchy of custom exceptions for your tool (`MyToolError → ConfigError, NetworkError, ...`) so callers can catch what they actually care about.
- **Use `try/finally` or context managers** for any resource (file, socket, lock, subprocess). `with` is not optional — it's how you avoid leaks.
- **Don't catch and silently swallow.** At minimum, log it. If it's truly ignorable, comment why.
- **Validate inputs at the boundary, trust them inside.** Argparse and Pydantic are good places to fail fast on bad input.

### 2.6 Logging

- **Use the `logging` module, not `print`.** Print statements are debugging artifacts; logging is observable infrastructure.
- **Configure logging once, at the entry point.** Library code calls `logger = logging.getLogger(__name__)` and never configures handlers itself.
- **Log structured data when possible** — JSON logs with `python-json-logger` or `structlog` are dramatically easier to query in aggregated systems (Splunk, ELK, CloudWatch).
- **Levels mean things.** `DEBUG` for traces, `INFO` for milestones, `WARNING` for recoverable oddities, `ERROR` for failures, `CRITICAL` for "page someone."

### 2.7 Subprocess and OS interaction

- **Use `subprocess.run`, never `os.system`.** `os.system` is a security and quoting disaster.
- **Pass arguments as a list, not a string** — `subprocess.run(["git", "status"])`, not `subprocess.run("git status", shell=True)`. `shell=True` invites injection bugs.
- **Always check exit codes.** Either `check=True` (raises on non-zero) or inspect `result.returncode` deliberately.
- **Capture output explicitly.** `capture_output=True, text=True` gives you `result.stdout` as a string. Default behavior leaks output to the parent process.
- **Set timeouts** on anything that talks to a network or could hang: `subprocess.run(..., timeout=30)`.
- **For cross-platform OS work, prefer libraries over shell-outs.** `shutil.copy` beats calling `cp`/`copy`. `psutil` beats parsing `ps` or `tasklist`. `pathlib` beats string manipulation of paths.

### 2.8 Concurrency and parallelism

Python's concurrency model is no longer the GIL-bottlenecked story it used to be (Python 3.13 ships an experimental no-GIL build), but choose the right tool:

| Workload | Tool |
|---|---|
| Many independent network/file I/O calls | `asyncio` with `httpx`, `aiofiles` |
| Moderate I/O, simpler code | `concurrent.futures.ThreadPoolExecutor` |
| CPU-bound work across cores | `concurrent.futures.ProcessPoolExecutor` or `multiprocessing` |
| Numeric work | NumPy / Polars vectorized ops — almost always faster than any concurrency |

Rule of thumb: if you find yourself writing manual `Thread` or `Process` objects, you're at the wrong abstraction level. Use the executor APIs.

### 2.9 Performance optimization

In order of cost-effectiveness:

1. **Measure first.** Use `cProfile`, `py-spy`, or `time.perf_counter()`. Don't optimize what you haven't measured.
2. **Pick a better algorithm.** O(n²) → O(n log n) beats every micro-optimization.
3. **Use built-ins and the standard library.** `sum()`, `set` operations, `dict.get`, `collections.Counter` are written in C.
4. **Vectorize with NumPy or Polars** for numeric / dataframe work. A `pandas.apply` with a Python lambda is usually the slow path; the vectorized equivalent can be 100× faster.
5. **Cache.** `functools.lru_cache` on pure functions is one line for a large win.
6. **Stream, don't materialize.** Generators, `csv.DictReader`, `polars.scan_csv()` (lazy) instead of loading everything.
7. **Only then** consider Cython, Rust extensions (PyO3), or rewriting hotspots. By this point you've usually fixed the real problem.

### 2.10 Security

- **Never `pickle` untrusted data.** Pickle deserialization executes arbitrary code. Use JSON for data interchange.
- **Never use `shell=True` with user input.** Quoting is hard; injection is easy. Lists of arguments don't have this problem.
- **Use `secrets` for tokens, not `random`.** `random` is predictable.
- **Don't log secrets.** Filter credentials before they hit log handlers.
- **Use `requests`/`httpx` with `verify=True`** (the default). Don't disable certificate verification to "make it work."
- **Pin dependencies with hashes** (`uv` does this in the lockfile) and audit periodically (`uv pip audit` or `pip-audit`).
- **Read `.env` files via `python-dotenv` for dev, real secret stores for prod** (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault). Don't commit `.env`.

### 2.11 Testing

- **pytest, not unittest.** It's the de facto standard, fixtures are vastly more usable, and the assertion introspection is far better.
- **Test the core, not the shell.** If logic lives in pure functions, tests are trivial. If your only function is 400 lines mixed with file I/O, tests are painful — that's a code smell.
- **Use `pytest` markers** (`@pytest.mark.slow`, `@pytest.mark.integration`) so CI can run fast unit tests on every commit and slow integration tests on a schedule.
- **Mock external services with `unittest.mock` or `respx`/`responses`** for HTTP. Real network calls in tests are flaky and slow.
- **Aim for coverage of behavior, not lines.** 100% line coverage of a function with no edge-case tests is theater.
- **Property-based testing with Hypothesis** is excellent for parsers, validators, and data transformations. It finds bugs your example-based tests will not.

### 2.12 CI/CD

A minimum-viable Python CI job in 2026:

```yaml
- run: uv sync --frozen          # Install from lockfile, fail if drift
- run: uv run ruff check .       # Lint
- run: uv run ruff format --check .  # Format gate
- run: uv run ty check           # Type check (or: mypy / pyright)
- run: uv run pytest             # Tests
```

Notes:
- `uv sync` on a populated cache is sub-second; this loop is fast enough to run on every push.
- Cache the `uv` cache directory between runs.
- Run on Linux for speed, but matrix on Windows + macOS if your tool is meant to be cross-platform.
- For Azure Pipelines, use `UsePythonVersion@0` to pin the interpreter, then `uv sync`.

### 2.13 Anti-patterns to avoid

- **`pip install` directly into system Python.** Always use a venv (or let `uv` manage it).
- **`requirements.txt` without a lockfile.** Reproducibility is not optional.
- **`from module import *`.** Hides what's in scope and breaks tooling.
- **Mutable default arguments** (`def f(x=[])`). Classic Python footgun — the list is shared across calls.
- **Bare `except:`** without a specific type. Catches `KeyboardInterrupt` and `SystemExit` too.
- **`os.path` strings.** Use `pathlib`.
- **String-formatted SQL.** Use parameterized queries always. Always.
- **Multi-thousand-line scripts in one file.** Split by concern. If `main.py` is 3,000 lines, `core/` should exist.
- **Hand-rolled config parsing.** Use `tomllib` (built-in for `.toml`), `pydantic-settings`, or `argparse`.
- **Blocking calls in async code.** `time.sleep()` inside an `async def` is a deadlock waiting to happen. Use `await asyncio.sleep()`.
- **Catching exceptions to make linters quiet.** That's not handling — that's hiding.

### 2.14 Quick reference

```bash
# Bootstrap a new project
uv init my-tool && cd my-tool
uv add requests httpx
uv add --dev ruff pytest ty

# Daily loop
uv run ruff check --fix .       # Lint + autofix
uv run ruff format .            # Format
uv run ty check                 # Type check
uv run pytest                   # Test
uv run python -m my_tool        # Run the tool

# Add a tool ad-hoc, no install
uvx ruff check .

# Update deps
uv lock --upgrade
uv sync

# Run a one-off script with inline deps (PEP 723)
uv run script.py
```

---

## Summary

Python is the right answer when the work crosses operating systems, leans on libraries, involves real data or real logic, or will outgrow being "just a script." It is the wrong answer when the task lives entirely on Windows admin surfaces or when "I just need to run one command" is the actual requirement.

When you do choose Python, the modern stack is small and opinionated: **uv** for everything package-shaped, **Ruff** for everything style-shaped, **pytest** for tests, type hints throughout, `pyproject.toml` as the single config file. Most of what made Python painful in 2021 has been collapsed into one or two tools. Use them.
