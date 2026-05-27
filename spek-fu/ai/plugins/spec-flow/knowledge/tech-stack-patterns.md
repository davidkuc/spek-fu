# Tech Stack Patterns

Canonical reference for spec-flow implementation setup and build/test discovery.

Use this file when a skill needs to:
- decide which ignore files to verify or create
- determine the essential ignore patterns for a detected stack
- map build manifests to the build/test command family

## Universal Patterns

Always include these ignore patterns when the corresponding ignore file exists or is being created:

- `.DS_Store`
- `Thumbs.db`
- `*.tmp`
- `*.swp`
- `.vscode/`
- `.idea/`

## Node.js / TypeScript

### Ignore Patterns

- `node_modules/`
- `dist/`
- `build/`
- `coverage/`
- `*.log`
- `.env*`

### Build/Test Discovery

- Manifests: `package.json`
- Build command family: prefer the repository-defined package-manager command for `build`; default to `npm run build` when a `build` script exists
- Test command family: prefer the repository-defined package-manager command for `test`; default to `npm test` when a `test` script exists

## Python

### Ignore Patterns

- `__pycache__/`
- `*.pyc`
- `.venv/`
- `venv/`
- `dist/`
- `*.egg-info/`
- `.pytest_cache/`

### Build/Test Discovery

- Manifests: `pyproject.toml`, `setup.py`, `setup.cfg`
- Build command family: use the repository-defined packaging or build command when present; otherwise no build step is required by default
- Test command family: prefer the repository-defined test command; default to `pytest` when the repo uses pytest

## Java

### Ignore Patterns

- `target/`
- `*.class`
- `*.jar`
- `.gradle/`
- `build/`

### Build/Test Discovery

- Manifests: `pom.xml`, `build.gradle`, `build.gradle.kts`
- Build command family: `mvn package` for Maven or `gradle build` for Gradle when those tools are in use
- Test command family: `mvn test` for Maven or `gradle test` for Gradle

## .NET / C#

### Ignore Patterns

- `bin/`
- `obj/`
- `*.user`
- `*.suo`
- `packages/`

### Build/Test Discovery

- Manifests: `*.sln`, `*.csproj`
- Build command family: `dotnet build`
- Test command family: `dotnet test`

## Go

### Ignore Patterns

- `*.exe`
- `*.test`
- `vendor/`
- `*.out`
- `coverage.out`

### Build/Test Discovery

- Manifests: `go.mod`
- Build command family: `go build ./...`
- Test command family: `go test ./...`

## Rust

### Ignore Patterns

- `target/`
- `debug/`
- `release/`
- `*.rs.bk`
- `*.rlib`

### Build/Test Discovery

- Manifests: `Cargo.toml`
- Build command family: `cargo build`
- Test command family: `cargo test`

## Docker-Adjacent Files

When Docker is detected from `Dockerfile*`, container manifests, or explicit research notes:

- verify or create `.dockerignore`
- include stack-specific build outputs and the universal patterns when relevant

## Extension Rules

When adding a new stack:
1. Add a top-level section named for the stack.
2. Define the required ignore patterns first.
3. List the build manifest filenames that identify the stack.
4. Record the preferred build and test command family.
5. Keep stack-specific data here rather than duplicating it in skill files.