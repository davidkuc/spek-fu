# PowerShell Scripting Guide

A guide for engineers in mixed-OS environments. Part 1 helps you decide *whether* PowerShell is the right tool for the task. Part 2 covers *how* to use it well once you've decided.

> **Companion document:** `python-scripting-guide.md`. The two guides are structured identically — read them side-by-side when a task is genuinely ambiguous.

> **Version note:** This guide assumes **PowerShell 7.4 LTS or 7.5+** (`pwsh`). Windows PowerShell 5.1 is in legacy support only — Microsoft has signaled the end of feature work, and any script being newly authored should target PowerShell 7. If your environment still runs 5.1 in places, the guidance here is still your target state.

---

## Part 1 — When to Choose PowerShell (Assessment)

### 1.1 PowerShell's identity in one paragraph

PowerShell is a **shell first, a scripting language second**. Its defining feature is the *object pipeline*: cmdlets pass typed .NET objects between stages, not text streams. That single design choice is what makes PowerShell the right tool for system administration — you filter on properties, not regex; you sort by date, not column position; you call methods on objects directly. PowerShell's leverage comes from three things: deep, native integration with Windows and Microsoft platforms; a verb-noun cmdlet vocabulary that is self-documenting and discoverable; and the ability to drop down to .NET whenever you need more horsepower.

### 1.2 Strong-fit signals — pick PowerShell

If two or more of these apply, PowerShell is almost certainly the right tool:

- **The task targets Windows admin surfaces** — Active Directory, Group Policy, Windows services, the registry, event logs, scheduled tasks, IIS, Hyper-V, WMI/CIM, certificates.
- **The task targets Microsoft 365 / Microsoft Graph admin** — Exchange Online, SharePoint Online, Teams, Intune. Official, mature modules exist for all of these.
- **The task is Azure infrastructure work** and your team is already in the Microsoft ecosystem — the `Az` module is first-class, updated in lockstep with the platform, and friendlier than `azure-cli` for stateful, multi-step operations.
- **The work is interactive system exploration** — you're at a console, you need to see what's running, what's listening on a port, who has what permission, and you'll script up whatever you discover. This is PowerShell's home turf.
- **You're glueing together command-line tools and Windows APIs** in a CI/CD step — environment variables, file system, calling MSI installers, configuring IIS, signing binaries. PowerShell minimizes the moving parts on a Windows agent.
- **The pipeline already runs PowerShell** (Azure DevOps `PowerShell@2` tasks, build agents using `pwsh`). Adding Python is a runtime dependency that needs to earn its place.
- **A PowerShell module already does most of the work.** Re-implementing AD or Exchange operations in another language usually means shelling out to PowerShell anyway — write the script in PowerShell directly.
- **You need PowerShell-specific features**: Desired State Configuration (DSC), JEA (Just Enough Administration), constrained endpoints, signed scripts under `AllSigned` execution policy.

### 1.3 Weak-fit signals — reconsider

If two or more of these apply, Python (or sometimes Bash) is probably the better choice:

- The task is **heavily data-oriented** — numerical analysis, dataframes, statistical work, ML. PowerShell can do basic data shaping, but it's nobody's idea of a data tool.
- The task targets **Linux-only or container-native infrastructure** with no Windows component. PowerShell 7 runs there, but you'll be the only person on the team writing it that way.
- The work needs **rich third-party libraries** that exist in Python's ecosystem and not PowerShell's — ML frameworks, scientific computing, network device automation (Netmiko/NAPALM), Selenium.
- The script will **grow into a service or a packaged application**. PowerShell is excellent for scripts and modules; it is not where you build a web service or a long-running daemon.
- The team is **mostly developers without a Windows admin background**. PowerShell's syntax is unfamiliar to them, and the maintenance burden falls on a smaller pool.
- You'd be **fighting the language** — implementing complex algorithms, building DSLs, doing heavy text munging. These are doable but not what PowerShell is best at.

### 1.4 Decision questions (use in this order)

1. **Does the core work happen on Windows admin surfaces (AD, Exchange, registry, services, GPO, M365)?** → PowerShell.
2. **Will this run on more than one OS, with no Windows-specific work?** → Python.
3. **Is the work mostly orchestrating cmdlets, CLI tools, and `.exe` installers?** → PowerShell.
4. **Is the work data-heavy, algorithmic, or library-heavy?** → Python.
5. **Is there an existing solution in one of the languages?** → Don't rewrite. Use what works and integrate at a clean boundary.
6. **None of the above gave a clear answer?** → Pick the language your team knows best. Both can do most general-purpose tasks adequately.

### 1.5 Decision matrix

| Scenario | Lean PowerShell | Lean Python |
|---|---|---|
| Active Directory user provisioning | ✅ | ❌ |
| Exchange / Microsoft 365 admin | ✅ | ❌ |
| Azure resource management (Az module) | ✅ | ⚠️ Possible via SDK |
| Windows registry / event log manipulation | ✅ | ❌ |
| IIS / Windows Server configuration | ✅ | ❌ |
| One-off ad-hoc shell task on Windows | ✅ | ⚠️ Heavy |
| Cross-platform CLI tool | ❌ | ✅ |
| Multi-cloud automation (AWS + Azure + GCP) | ⚠️ Az is great; AWS/GCP thinner | ✅ |
| Log parsing & analytics across many servers | ⚠️ OK for moderate jobs | ✅ |
| REST API client that becomes a service | ❌ | ✅ |
| Build/test orchestration on Windows agents | ✅ | ⚠️ Possible |
| ML training pipeline | ❌ | ✅ |
| Embedding scripting into a third-party app | ❌ | ✅ |
| DSC / JEA / constrained admin endpoints | ✅ | ❌ |
| Network device automation | ❌ | ✅ |

### 1.6 The mixing rule

Use both, but never mix them inside the same script for the same concern. The healthy pattern is **one orchestrator language, with the other invoked at a clearly defined boundary**. For example: a PowerShell pipeline step that calls `python train.py` and reads its stdout, or a Python tool that calls `pwsh -Command Get-ADUser ...` for one specific Windows-only fetch and parses the JSON result. Avoid scripts where reading them requires fluency in both.

---

## Part 2 — Best Practices and Optimizations

### 2.1 The 2026 baseline

| Concern | Tool / Practice |
|---|---|
| Runtime | **PowerShell 7.4 LTS or 7.5+** (`pwsh`), not Windows PowerShell 5.1 |
| Linting / static analysis | **PSScriptAnalyzer** (`Invoke-ScriptAnalyzer`) |
| Formatting | PSScriptAnalyzer formatter (built into the VS Code extension) |
| Testing | **Pester 5.x** (the v5 syntax — discovery / run separation) |
| Editor | VS Code with the official PowerShell extension |
| Package source | PowerShell Gallery (`Install-Module`) and your internal feed |
| Module manifest | `.psd1` with explicit `RequiredModules`, `PowerShellVersion = '7.4'`, `CompatiblePSEditions` |
| Version control | All scripts and modules in Git, full stop |

If any production script or module is still pinned to Windows PowerShell 5.1, treat its migration to 7.x as planned work, not a side quest. PS7's pipeline is faster, error handling is cleaner, parallel features exist, and 5.1 is no longer receiving meaningful improvements.

### 2.2 Cmdlet and function naming

- **Use the approved verb-noun convention.** `Verb-Noun`, singular noun. `Get-User`, not `GetUsers`. Run `Get-Verb` to see the approved list.
- **Use approved verbs.** PSScriptAnalyzer's `PSUseApprovedVerbs` rule will tell you when you've drifted (e.g., `Create-` should be `New-`, `Delete-` should be `Remove-`).
- **Prefix nouns to avoid collisions.** A function in your `Acme.IAM` module should be `Get-AcmeUser`, not `Get-User`. This becomes critical when modules from different sources end up in the same session.
- **Don't use aliases in scripts.** `%`, `?`, `gci`, `select` are great interactively. In a script, write `ForEach-Object`, `Where-Object`, `Get-ChildItem`, `Select-Object`. PSScriptAnalyzer rule: `PSAvoidUsingCmdletAliases`.
- **Don't use positional parameters in scripts.** `Get-ChildItem -Path C:\Logs -Filter *.log` is readable in a year. `gci C:\Logs *.log` is not.

### 2.3 Advanced functions — the right shape

Every non-trivial function should be an **advanced function**: `[CmdletBinding()]` plus a `param()` block with attributes. This unlocks `-Verbose`, `-WhatIf`, `-ErrorAction`, parameter validation, pipeline binding, and tab completion for free.

```powershell
function Set-AcmeUserStatus {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
    param(
        [Parameter(Mandatory, ValueFromPipeline, ValueFromPipelineByPropertyName)]
        [ValidateNotNullOrEmpty()]
        [string[]] $UserName,

        [Parameter(Mandatory)]
        [ValidateSet('Active', 'Disabled', 'Locked')]
        [string] $Status
    )

    begin {
        Write-Verbose "Beginning status update to '$Status'"
    }

    process {
        foreach ($name in $UserName) {
            if ($PSCmdlet.ShouldProcess($name, "Set status to $Status")) {
                # ...do the work...
                [pscustomobject]@{
                    UserName = $name
                    Status   = $Status
                    Time     = Get-Date
                }
            }
        }
    }
}
```

Things that earn their keep here:

- **`SupportsShouldProcess` + `ShouldProcess()`** gives you `-WhatIf` and `-Confirm` for free. Mandatory for any function that mutates state.
- **`ConfirmImpact = 'High'`** prompts by default for destructive operations.
- **Parameter validation attributes** (`ValidateNotNullOrEmpty`, `ValidateSet`, `ValidateRange`, `ValidatePattern`, `ValidateScript`) catch bad input before the function runs.
- **`ValueFromPipeline` / `ValueFromPipelineByPropertyName`** makes the function composable with the rest of the shell.
- **`begin / process / end` blocks** are required for pipeline functions — `process` runs once per piped item.
- **Output a single, clean object type** — usually `[pscustomobject]`. Don't `Write-Host` results; emit them so the caller can pipe, filter, format, and export.

### 2.4 Output, the cardinal rule

- **`Write-Output` (or just emit) for results.** This is the only stream a caller can pipe.
- **`Write-Verbose` for narration.** Visible only with `-Verbose`.
- **`Write-Warning` for recoverable concerns.**
- **`Write-Error` for non-terminating errors.** Or `throw` for terminating ones.
- **`Write-Information` for user-facing messages** that aren't part of the data result.
- **`Write-Debug` for deep diagnostics.**
- **Never `Write-Host` to communicate data.** It writes to the host display only and is invisible to the pipeline. It's fine for a deliberate banner or a colored console message that should never be captured.

A function that mixes results and chatter into a single output stream is broken — its caller can't filter, sort, export, or test it.

### 2.5 Error handling

PowerShell has two error modes — **terminating** and **non-terminating** — and most subtle bugs come from confusing them.

- **Cmdlets emit non-terminating errors by default.** They appear in `$Error` but execution continues. To make them terminating: `-ErrorAction Stop`.
- **`try/catch` only catches terminating errors.** A `try { Get-ChildItem nope }` will *not* enter the `catch` unless you add `-ErrorAction Stop`.
- **Native commands (`.exe`) do not throw.** Check `$LASTEXITCODE` after every native call. PowerShell 7.4+ adds `$PSNativeCommandUseErrorActionPreference = $true` which makes native commands honor `$ErrorActionPreference` — turn it on.
- **Catch specific exception types**, not bare `catch`:

  ```powershell
  try {
      Get-Content $Path -ErrorAction Stop
  }
  catch [System.IO.FileNotFoundException] {
      Write-Warning "File missing: $Path"
  }
  catch {
      Write-Error "Unexpected: $($_.Exception.Message)"
      throw
  }
  ```
- **Re-throw with `throw`** when you've logged but can't recover. Don't swallow.
- **Use `$PSCmdlet.ThrowTerminatingError(...)`** in advanced functions when you need a clean terminating error that integrates with the calling cmdlet's error stream.

### 2.6 The pipeline, used well

The pipeline is the single biggest reason to use PowerShell. Use it deliberately.

- **Filter left, format right.** Filtering early discards data before it travels through the pipeline.
- **Prefer cmdlet-native filters over `Where-Object` when available.** `Get-ChildItem -Filter *.log` is dramatically faster than `Get-ChildItem | Where-Object Name -like '*.log'` because `-Filter` pushes the predicate down to the file system provider.
- **Use `Where-Object` for property comparisons,** not parameter filters: `Get-Process | Where-Object WorkingSet -gt 100MB`.
- **Use `Select-Object` to project,** `Sort-Object` to order, `Group-Object` to bucket, `Measure-Object` to summarize. Learn these four cold.
- **Avoid `Format-*` until the very end.** `Format-Table` produces formatting objects that are useless for further processing. If you ever pipe `Format-Table` into anything else, you have a bug.
- **Use `[pscustomobject]`** for ad-hoc shaped output — it's ordered, fast, and the universal "row" type.

### 2.7 Performance

PowerShell can be fast or slow by orders of magnitude depending on idiom. Top wins:

1. **Don't grow arrays with `+=` in a loop.** This reallocates on every append — O(n²). Use `[System.Collections.Generic.List[object]]::new()` and `.Add()`, or let the pipeline build the result for you.

   ```powershell
   # ❌ Slow
   $results = @()
   foreach ($x in 1..10000) { $results += [pscustomobject]@{ Value = $x } }

   # ✅ Fast
   $results = [System.Collections.Generic.List[pscustomobject]]::new()
   foreach ($x in 1..10000) { $results.Add([pscustomobject]@{ Value = $x }) }

   # ✅ Also fast (and idiomatic)
   $results = foreach ($x in 1..10000) { [pscustomobject]@{ Value = $x } }
   ```

2. **`foreach` statement vs `ForEach-Object` cmdlet.** The statement (`foreach ($x in $coll)`) is several times faster than the cmdlet for in-memory collections, because there's no pipeline machinery. Use the cmdlet when you genuinely need pipeline streaming; use the statement for everything else.

3. **Use .NET methods for hot loops.** `[System.IO.File]::ReadAllLines($path)` reads a file dramatically faster than `Get-Content` for large files. `Get-Content -ReadCount 0` is also good — it returns the whole file as one operation.

4. **`ForEach-Object -Parallel` for I/O-bound work** (PS 7+). Each iteration runs in its own runspace.

   ```powershell
   $servers | ForEach-Object -Parallel {
       $name = $_
       $svc  = $using:serviceName
       Invoke-Command -ComputerName $name -ScriptBlock { Get-Service $using:svc }
   } -ThrottleLimit 16
   ```

   Notes:
   - **Use `$using:varname`** to reference outer-scope variables. Plain `$varname` won't see them — runspaces are isolated.
   - **Set `-ThrottleLimit` deliberately.** For CPU-bound work, ~= logical core count. For I/O-bound work (HTTP, ping, remoting), 2–3× cores or more.
   - **Don't parallelize trivial work.** Spinning up runspaces has real overhead; if each iteration is 5ms, parallel will be slower than sequential.
   - **Aggregate with thread-safe collections** — `[System.Collections.Concurrent.ConcurrentBag[object]]::new()` — when iterations need to share state.

5. **Use `Start-ThreadJob`** for fire-and-forget async work. It's lighter than `Start-Job` (which spawns a new process).

6. **Cache `Get-` calls.** `Get-ADUser` is expensive. If a script needs the same data twice, store it in a variable.

7. **Measure with `Measure-Command`.** Don't guess at performance — measure.

### 2.8 Modules and project structure

Once a related set of functions exceeds a few dozen lines, build a module.

```
Acme.IAM/
├── Acme.IAM.psd1              # Module manifest (use New-ModuleManifest)
├── Acme.IAM.psm1              # Root module — typically dot-sources everything below
├── Public/                    # One function per file, exported
│   ├── Get-AcmeUser.ps1
│   └── Set-AcmeUserStatus.ps1
├── Private/                   # Internal helpers, not exported
│   └── Invoke-AcmeApi.ps1
├── Tests/                     # Pester tests, mirroring Public/Private layout
│   ├── Get-AcmeUser.Tests.ps1
│   └── Set-AcmeUserStatus.Tests.ps1
└── README.md
```

In the manifest (`.psd1`):

- Set `PowerShellVersion = '7.4'` and `CompatiblePSEditions = @('Core')` if you're 7-only. Add `'Desktop'` only if the module genuinely supports 5.1.
- Set `RequiredModules` explicitly with version constraints — don't rely on whatever happens to be in `$env:PSModulePath`.
- Set `FunctionsToExport` to an explicit list, not `'*'`. Wildcards prevent module auto-discovery from working efficiently.
- Provide `Description`, `Author`, `CompanyName`, and a project URL.

### 2.9 Security

- **Use `[pscredential]`, never plain-text passwords.** PSScriptAnalyzer's `PSAvoidUsingPlainTextForPassword` and `PSAvoidUsingUserNameAndPasswordParams` enforce this.
- **Read secrets from a vault** — `SecretManagement` module + a vault provider (Azure Key Vault, KeePass, HashiCorp Vault). Never commit secrets, never write them to log files.
- **Avoid `Invoke-Expression`.** It evaluates an arbitrary string as PowerShell code — every input becomes a potential injection vector. PSScriptAnalyzer will flag it. There is almost always a better approach (a `ScriptBlock`, a hashtable lookup, a switch statement).
- **Sign your scripts** for production use, and run with `Set-ExecutionPolicy AllSigned` (or stricter) on servers. `Bypass` and `Unrestricted` should not exist in production.
- **Use Constrained Language Mode and JEA** when granting privileged access — don't hand out full admin shells when a constrained role-capability endpoint will do.
- **Use `SupportsShouldProcess`** on every destructive function so callers can dry-run with `-WhatIf`. This is a security control and a debugging tool simultaneously.
- **Validate parameters at the boundary.** `[ValidateScript({...})]`, `[ValidatePattern(...)]`, `[ValidateSet(...)]` are how you fail fast on bad input.

### 2.10 Cross-platform PowerShell

If your script runs on multiple OSes:

- **Use `Join-Path`, never string concatenation,** for paths.
- **Don't hard-code drive letters.** `C:\Temp` doesn't exist on Linux. Use `$env:TEMP`, `[System.IO.Path]::GetTempPath()`, or `~`.
- **Branch on `$IsWindows`, `$IsLinux`, `$IsMacOS`** for OS-specific work. These are automatic variables in PowerShell 7+.
- **Avoid Windows-only modules** in cross-platform code paths: `ActiveDirectory`, `GroupPolicy`, anything calling COM, anything calling `Get-WmiObject` (use `Get-CimInstance` instead, and verify the CIM class exists on your target).
- **Use UTF-8 explicitly.** PowerShell 7 defaults to UTF-8, but be defensive: `Out-File -Encoding utf8`, `Set-Content -Encoding utf8`. Don't rely on platform defaults.
- **Test on each target OS in CI.** "Should work on Linux" is not the same as "tested on Linux."

### 2.11 Testing with Pester 5

- **Pester 5 separates discovery from run.** Top-level code in a `.Tests.ps1` runs at *discovery* time; assertions inside `It` blocks run at *run* time. Reading a Pester 4 script as if it's Pester 5 will lead you astray.
- **Use `BeforeAll` / `BeforeEach` for setup.** Variables set there are available inside `It` blocks.
- **Mock at the right level.** `Mock Invoke-RestMethod` to keep tests offline. Never make real HTTP calls in unit tests.
- **Use `Should -Throw`, `Should -Be`, `Should -BeOfType`** for assertions. The Pester 5 syntax with `-` prefixes is the supported form.
- **Run PSScriptAnalyzer as a Pester test** so style violations fail the build the same way unit failures do.
- **Configure via `New-PesterConfiguration`**, not by passing a dozen parameters to `Invoke-Pester`. The hashtable-based config from old examples is deprecated.

A minimum example:

```powershell
BeforeAll {
    . $PSCommandPath.Replace('.Tests.ps1', '.ps1')
}

Describe 'Get-AcmeUser' {
    It 'returns a user object' {
        Mock Invoke-RestMethod { @{ id = 1; name = 'alice' } }
        $u = Get-AcmeUser -Name 'alice'
        $u.name | Should -Be 'alice'
        Should -Invoke Invoke-RestMethod -Times 1
    }
}
```

### 2.12 CI/CD

A minimum-viable PowerShell CI job:

```yaml
- pwsh: |
    Install-Module PSScriptAnalyzer, Pester -Force -Scope CurrentUser
    Invoke-ScriptAnalyzer -Path ./src -Recurse -Settings PSGallery -Severity Error,Warning |
        Tee-Object -Variable lint
    if ($lint) { throw "$($lint.Count) lint violation(s)" }

- pwsh: |
    $cfg = New-PesterConfiguration
    $cfg.Run.Path = './Tests'
    $cfg.Run.Exit = $true
    $cfg.TestResult.Enabled = $true
    $cfg.TestResult.OutputFormat = 'NUnitXml'
    $cfg.TestResult.OutputPath = 'pester-results.xml'
    $cfg.CodeCoverage.Enabled = $true
    Invoke-Pester -Configuration $cfg
```

Notes:

- **Use `pwsh`, not `powershell`,** in your YAML. `powershell` invokes Windows PowerShell 5.1 on Windows agents.
- **Pin module versions** if you need reproducibility: `Install-Module Pester -RequiredVersion 5.7.0`.
- **Cache the modules directory** between runs to avoid re-downloading every build.
- In Azure DevOps, prefer the `PowerShell@2` task (cross-platform, uses `pwsh`) over the older `PowerShell@1` (Windows PowerShell only) and over `AzurePowerShell@5` for non-Az work.
- Run PSScriptAnalyzer first — it's fast and catches the cheapest class of failures.

### 2.13 Anti-patterns to avoid

- **`Write-Host` for results.** Use `Write-Output` (or just emit). `Write-Host` is for the human at the console only.
- **`+=` to grow arrays.** O(n²). Use a `List<T>` or let the pipeline build the array.
- **`%{...}` and `?{...}` aliases in committed scripts.** Use `ForEach-Object` and `Where-Object`. PSScriptAnalyzer rule: `PSAvoidUsingCmdletAliases`.
- **Bare `catch {}` that swallows errors.** At minimum log; usually re-throw.
- **`Invoke-Expression` on user-controlled input.** Code injection.
- **Plain-text passwords in parameters.** Use `[pscredential]` or `[securestring]`.
- **Functions without `[CmdletBinding()]`.** You're throwing away `-Verbose`, `-WhatIf`, validation, and pipeline support.
- **`Get-WmiObject`.** Deprecated. Use `Get-CimInstance` — it's cross-platform-friendly and faster.
- **Manual JSON construction by string interpolation.** Use `ConvertTo-Json` and `ConvertFrom-Json`. Manual JSON is a security and correctness hazard.
- **Functions that both compute and `Format-Table` their result.** Now the caller can't pipe it. Compute and emit objects; let formatting happen at the console.
- **Long, monolithic `.ps1` files** with 50 functions. Build a module. Split by concern.
- **Unbounded `ForEach-Object -Parallel` on cheap iterations.** Runspace overhead exceeds savings. Benchmark first.
- **Relying on `$Error[0]`** instead of catching specifically. `$Error` is convenient at the console but a fragile basis for control flow in scripts.
- **Mixing PS 5.1 and PS 7 syntax** in one script. Pick a target version, declare it in the manifest, test against it.

### 2.14 Quick reference

```powershell
# Discoverability
Get-Command -Module Az.Compute            # What does this module expose?
Get-Help Get-Process -Examples            # Show me usage
Get-Member -InputObject (Get-Process)[0]  # What properties/methods does this object have?

# Daily loop
Invoke-ScriptAnalyzer -Path . -Recurse                                # Lint
Invoke-Pester -Path ./Tests                                            # Test
Get-Module -ListAvailable Acme.*                                       # What's installed?

# Useful patterns
$results = $items | ForEach-Object -Parallel { Process-Item $_ } -ThrottleLimit 16
$users   | Where-Object Department -eq 'Sales' | Select-Object Name, Email | Sort-Object Name
Get-Content big.log -ReadCount 1000 | ForEach-Object { ... }           # Stream a large file in chunks
[pscustomobject]@{ Time = Get-Date; Status = 'OK'; Detail = $msg }     # Shaped output

# Module work
New-ModuleManifest -Path ./Acme.IAM/Acme.IAM.psd1 -RootModule Acme.IAM.psm1 -PowerShellVersion '7.4'
Test-ModuleManifest ./Acme.IAM/Acme.IAM.psd1
Publish-Module -Path ./Acme.IAM -Repository AcmeInternal
```

---

## Summary

PowerShell is the right answer when the work touches Windows admin surfaces, Microsoft 365, Azure, or any task where the object pipeline genuinely earns its keep. It is the wrong answer for data-heavy work, library-heavy work, or scripts that are fundamentally cross-platform with no Windows component.

When you do choose PowerShell, the modern shape of a good script is small and consistent: **PowerShell 7.x**, advanced functions with `[CmdletBinding()]` and `SupportsShouldProcess`, parameter validation, output as objects (never `Write-Host`), errors handled by exception type, performance-aware idioms (`List<T>` over `+=`, `foreach` statement over the cmdlet for in-memory work, `-Parallel` for genuine I/O concurrency), modules over monolithic scripts, **PSScriptAnalyzer** in CI, **Pester 5** for tests. Most of what made PowerShell painful in 2018 has been fixed in 7.x. Use the new version.
